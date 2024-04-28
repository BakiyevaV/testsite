import logging
from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.paginator import Paginator
from django.db.transaction import atomic
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from psycopg2.extras import DateTimeTZRange

from .models import Tasks, Subscribes, Icecream, LimitedEditionIcecream
from .forms import TaskForm, StatusForm, IcecreamForm, TaskEditFormset, SearchForm, CaptchaTestForm, SubscribeForm
from django.views.decorators.http import require_http_methods
from django.db import transaction

from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime
from precise_bbcode.bbcode import get_parser

from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import UserCreateSerializer, TaskEditSerializer, TasksSerializer, SubscribeSerializer
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.views import APIView
from django.utils import timezone

logger = logging.getLogger('taskboard')


# Create your views here


@api_view(['GET'])
def api_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserCreateSerializer(users, many=True)
        return Response(serializer.data)


@require_http_methods(['GET', 'POST'])
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        cap_form = CaptchaTestForm(request.POST)
        if form.is_valid() and cap_form.is_valid():
            task, created = Tasks.actions.get_or_create(implementer=form.cleaned_data['implementer'],
                                                        author=form.cleaned_data['author'],
                                                        title=form.cleaned_data['title'],
                                                        description=form.cleaned_data['description'],
                                                        deadline=form.cleaned_data['deadline'],
                                                        )
            task.time_to_do = DateTimeTZRange(task.published, task.deadline)
            deadline_datetime = timezone.make_aware(datetime.combine(task.deadline, datetime.min.time()))
            task.time_allotted = deadline_datetime - task.published
            task.save()
            if task.description == "":
                desc = 'Описание отсутствует'
            else:
                desc = task.description
            logger.debug(
                f'Создание новой задачи: имя-{task.title}; автор-{task.author}; исполнитель-{task.implementer};'
                f'описание-{desc}; срок исполнения-{task.deadline}')
            return redirect('taskboard:all_tasks')
        else:
            logger.error('Данные формы не валидны!')
    else:
        form = TaskForm()
        cap_form = CaptchaTestForm()
    tasks = Tasks.actions.all()
    total_tasks_count = tasks.count()
    not_started_tasks_count = Tasks.actions.not_started_count()
    done_tasks_count = Tasks.actions.done_count()
    in_process_tasks_count = Tasks.actions.in_progress_count()

    context = {'form': form, 'tasks': tasks, 'total_tasks_count': total_tasks_count,
               'not_started_tasks_count': not_started_tasks_count,
               'done_tasks_count': done_tasks_count, 'in_process_tasks_count': in_process_tasks_count,
               'active_page': 'create task', 'title': 'Create new task', 'cap_form': cap_form}
    return render(request, 'new_task.html', context)

    # if request.method == 'POST':
    #     implementer = request.POST.get('implementer')
    #     author = request.POST.get('author')
    #     title = request.POST.get('title')
    #     deadline = request.POST.get('deadline')
    #     description = request.POST.get('description')
    #     print(description)
    #     task = Tasks(implementer=implementer, author=author, title=title,
    #                  deadline=deadline, description=description)
    #
    #     task.save()
    #     return redirect('taskboard:all_tasks')
    #
    # tasks = Tasks.objects.all()
    # total_tasks_count = tasks.count()
    # not_started_tasks_count = tasks.filter(status="n").count()
    # done_tasks_count = tasks.filter(status="d").count()
    # in_process_tasks_count = tasks.filter(status="p").count()
    # context = {'tasks': tasks, 'total_tasks_count': total_tasks_count,
    #                'not_started_tasks_count': not_started_tasks_count,
    #                'done_tasks_count': done_tasks_count, 'in_process_tasks_count': in_process_tasks_count,
    #            'active_page': 'create task', 'title': 'Create new task'}
    # return render(request, 'new_task.html', context)


# def get_all_tasks(request):
#     model = Tasks
#     total_tasks_count = Tasks.actions.count()
#     not_started_tasks_count = Tasks.actions.not_started_count()
#     done_tasks_count = Tasks.actions.done_count()
#     in_process_tasks_count = Tasks.actions.in_progress_count()
#     if request.method == 'POST':
#         form = SearchForm(request.POST)
#         if form.is_valid():
#             keyword = form.cleaned_data['keyword']
#             tasks = Tasks.actions.filter(title__icontains=keyword)
#             paginator = Paginator(tasks, per_page=2, orphans=0)
#             if 'page' in request.GET:
#                 page_num = request.GET['page']
#             else:
#                 page_num = 1
#             page = paginator.get_page(page_num)
#             context = {'form': form, 'tasks': page.object_list, 'page_obj': page, 'total_tasks_count': total_tasks_count,
#                        'not_started_tasks_count': not_started_tasks_count, 'done_tasks_count': done_tasks_count,
#                        'in_process_tasks_count': in_process_tasks_count, 'active_page': 'all tasks',
#                        'title': 'All tasks'}
#             return render(request, 'index.html', context)
#
#     else:
#         tasks = model.actions.order_by_title_length()
#         paginator = Paginator(tasks, per_page=2, orphans=0)
#         form = SearchForm()
#         if 'page' in request.GET:
#             page_num = request.GET['page']
#         else:
#             page_num = 1
#         page = paginator.get_page(page_num)
#         context = {'form': form, 'tasks': page.object_list, 'page_obj': page, 'total_tasks_count': total_tasks_count,
#                    'not_started_tasks_count': not_started_tasks_count, 'done_tasks_count': done_tasks_count,
#                    'in_process_tasks_count': in_process_tasks_count, 'active_page': 'all tasks',
#                    'title': 'All tasks'}
#         return render(request, 'index.html', context)


def get_all_tasks(request):
    form = SearchForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        keyword = form.cleaned_data['keyword']
        tasks = Tasks.actions.filter(title__icontains=keyword)
    else:
        tasks = Tasks.actions.order_by_title_length()
    total_tasks_count = Tasks.actions.count()
    not_started_tasks_count = Tasks.actions.not_started_count()
    done_tasks_count = Tasks.actions.done_count()
    in_process_tasks_count = Tasks.actions.in_progress_count()

    paginator = Paginator(tasks, per_page=3, orphans=0)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)

    context = {'form': form, 'tasks': page.object_list, 'page_obj': page, 'total_tasks_count': total_tasks_count,
               'not_started_tasks_count': not_started_tasks_count, 'done_tasks_count': done_tasks_count,
               'in_process_tasks_count': in_process_tasks_count, 'active_page': 'all tasks', 'title': 'All tasks'}

    return render(request, 'index.html', context)


class APITasks(generics.ListCreateAPIView):
    serializer_class = TasksSerializer

    def get_queryset(self):
        queryset = Tasks.actions.all()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_tasks_count = queryset.count()
        not_started_tasks_count = queryset.filter(status='not_started').count()
        done_tasks_count = queryset.filter(status='done').count()
        in_process_tasks_count = queryset.filter(status='in_progress').count()

        response_data = {
            'queryset': self.serializer_class(queryset, many=True).data,
            'total_tasks_count': total_tasks_count,
            'not_started_tasks_count': not_started_tasks_count,
            'done_tasks_count': done_tasks_count,
            'in_process_tasks_count': in_process_tasks_count
        }

        return Response(response_data)


@require_http_methods(['GET', 'POST'])
def about_task(request, task_id):
    model = Tasks
    task = model.actions.get(pk=task_id)
    if request.method == 'POST':
        logger.debug('Закрытие существующей задачи')
        form = StatusForm(request.POST, instance=task)
        if form.is_valid():
            status = form.cleaned_data['status']
            print("статус", status)
            model.actions.all().filter(pk=task_id).update(status=status)
            if status == 'd':
                model.actions.all().filter(pk=task_id).update(done_date=datetime.datetime.now())
            else:
                if model.actions.get(pk=task_id).done_date != None:
                    row = model.actions.get(pk=task_id)
                    row.done_date = None
                    row.save()
            return redirect(reverse('taskboard:about_task', args=[task_id]))
    else:
        form = StatusForm(instance=task)
    context = {'task': task, 'form': form, 'title': 'About task', 'active_page': 'About task'}
    return render(request, 'product-details.html', context)


def delete_task(request, task_id):
    task = Tasks.actions.get(pk=task_id)
    if task.description == "" or task.description == " ":
        desc = 'Описание отсутствует'
    else:
        desc = task.description
    logger.debug(f'Удаление задачи: имя-{task.title}; автор-{task.author}; исполнитель-{task.implementer};'
                 f'описание-{desc}; срок исполнения-{task.deadline}; статус-{task.get_status_display()}')
    task.delete()
    return redirect(reverse('taskboard:all_tasks'))


@require_http_methods(['POST'])
def save_subscribes(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        return redirect('taskboard:make_subscribe', email=email)


# class ApiSaveSubscribes(APIView):
#     def post(self, request):
#         serializer = SubscribeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_http_methods(['GET', 'POST'])
def make_subscribe(request, email=None):
    form = SubscribeForm()
    if request.method == 'POST':
        if email:
            subscribe, created = Subscribes.objects.get_or_create(email=email)
            form = SubscribeForm(request.POST)
            print(subscribe.pk)
            if form.is_valid():
                print(subscribe)
                sub_instance = form.save(commit=False)
                sub_instance.mail = subscribe
                sub_instance.save()
                return redirect(reverse('taskboard:all_tasks'))
            else:
                print(form.errors)  # Ошибки будут напечатаны в консоли сервера
    context = {'form': form, "title": "Create subscribe", "email": email}
    return render(request, 'make_subscribe.html', context)


def create_icecream(request):
    special_fields = ['theme', 'season', 'sale_start_date', 'sale_end_date', 'unique_flavors']
    if request.method == 'POST':
        icecream_form = IcecreamForm(request.POST)
        cap_form = CaptchaTestForm(request.POST)
        if icecream_form.is_valid() and cap_form.is_valid():
            icecream_form.save()
            return redirect('taskboard:icecream')
        else:
            icecream_form = IcecreamForm(request.POST)
            cap_form = CaptchaTestForm(request.POST)
            print('не проходит')
            context = {'message': 'Введены некорректные данные', 'title': 'Create icecream',
                       'icecream_form': icecream_form, 'cap_form': cap_form, 'active_page': 'create icecream',
                       'special_fields': special_fields}
            return render(request, 'create_icecream.html', context)

    else:
        icecream_form = IcecreamForm()
        cap_form = CaptchaTestForm()
    context = {'icecream_form': icecream_form, 'active_page': 'create icecream',
               'title': 'Create icecream', 'special_fields': special_fields, 'cap_form': cap_form}
    return render(request, 'create_icecream.html', context)


def get_icecream(request):
    icecream = LimitedEditionIcecream.objects.all()
    paginator = Paginator(icecream, per_page=2, orphans=0)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'icecream': icecream, 'page_obj': page, 'active_page': 'icecream', 'title': 'Icecream'}
    return render(request, 'index.html', context)


class apiEditTask(ModelViewSet):
    queryset = Tasks.actions.all()
    serializer_class = TaskEditSerializer


def edit_task(request):
    model = Tasks
    # if request.method == 'POST':
    #     formset = TaskEditFormset(request.POST,  queryset=model.actions.all())
    #     for form in formset.forms:
    #         if form.instance.deadline:
    #             form.initial['deadline'] = form.instance.deadline.strftime('%Y-%m-%d')
    #         if form.instance.done_date:
    #             form.initial['done_date'] = form.instance.done_date.strftime('%Y-%m-%d')
    #     if formset.is_valid():
    #         for form in formset:
    #             try:
    #                 form.save()
    #                 transaction.on_commit(commit_handler)
    #                 context = {'message': 'Изменения приняты', 'formset': formset, 'title': 'Edit task',
    #                            'active_page': 'Edit task'}
    #                 return render(request, 'edit_task.html', context)
    #             except:
    #                 transaction.rollback()
    #                 context = {'message': 'Что-то пошло не так', 'formset': formset, 'title': 'Edit task',
    #                            'active_page': 'Edit task'}
    #                 return render(request, 'edit_task.html', context)
    #     else:
    #         context = {'message': 'Введены некорректные данные', 'formset': formset, 'title': 'Edit task',
    #                    'active_page': 'Edit task'}
    #         transaction.commit()
    #         return render(request, 'edit_task.html', context)
    # else:
    formset = TaskEditFormset()
    for form in formset.forms:
        if form.instance.deadline:
            form.initial['deadline'] = form.instance.deadline.strftime('%Y-%m-%d')
        if form.instance.done_date:
            form.initial['done_date'] = form.instance.done_date.strftime('%Y-%m-%d')
    context = {'formset': formset, 'title': 'Edit task', 'active_page': 'Edit task'}
    return render(request, 'edit_task.html', context)


def commit_handler():
    print('Транзакция прошла успешно!')

# def search(request):
#     if request.method == 'POST':
#         sf = SearchForm(request.POST)
#         if sf.is_valid():
#             keyword = sf.cleaned_data['keyword']
#             rubric_id = sf.cleaned_data['rubric'].pk
#             tasks = Tasks.objects.filter(title__icontains=keyword)
#             context = {'tasks': tasks}
#             return render(request, 'bboard/search_results.html', context)
#     else:
#         sf = SearchForm()
#         context = {'form': sf}
#         return render(request, 'bboard/search.html', context)
























