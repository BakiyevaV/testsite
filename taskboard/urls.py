from django.contrib import admin
from django.urls import path

from taskboard.views import create_task, get_all_tasks, about_task, delete_task, save_subscribes, create_icecream, \
    get_icecream, edit_task, api_users, apiEditTask, APITasks, make_subscribe

from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register('tasks', apiEditTask, basename='tasks')

app_name = 'taskboard'

urlpatterns = [
    path('', get_all_tasks, name='all_tasks'),
    path('create_task/', create_task, name='create_task'),
    path('about_task/<int:task_id>/', about_task, name='about_task'),
    path('delete_task/<int:task_id>/', delete_task, name='delete_task'),
    path('subscribe/', save_subscribes, name='subscribe'),
    path('create_icecream/', create_icecream, name='create_icecream'),
    path('icecream/', get_icecream, name='icecream'),
    path('edit/', edit_task, name='edit_task'),
    path('api/users/', api_users),
    path('api/', include(router.urls)),
    path('api/tasks/', APITasks.as_view()),
    # path('api/subscribe/', ApiSaveSubscribes.as_view()),
    path('make_subscribe/<str:email>/', make_subscribe, name="make_subscribe"),

]



