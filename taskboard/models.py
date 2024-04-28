from django.contrib.auth.models import User, AbstractUser
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Length
from precise_bbcode.fields import BBCodeTextField
from django.contrib.postgres.fields import *
from localflavor.generic.models  import *



class TasksQuerySet(models.QuerySet):
    def order_by_title_length(self):
        return self.annotate(title_length=Length('title')).order_by('-title_length')

class TasksManager(models.Manager):
    def get_queryset(self):
        return TasksQuerySet(self.model, using=self._db)

    def order_by_title_length(self):
        return self.get_queryset().order_by_title_length()

    def not_started_count(self):
        return self.filter(status=Tasks.Status.not_started).count()

    def done_count(self):
        return self.filter(status=Tasks.Status.done).count()

    def in_progress_count(self):
        return self.filter(status=Tasks.Status.in_progress).count()

class Tasks(models.Model):
    class Status(models.TextChoices):
        not_started = 'n', 'Не начато'
        done = 'd', 'Исполнено'
        in_progress = 'p', 'На исполнении'

    actions = TasksManager()

    implementer = models.CharField(max_length=100, verbose_name="Исполнитель", null=True, blank=True)
    author = models.CharField(max_length=100, verbose_name="Автор задачи", null=True, blank=True)
    title = models.CharField(max_length=100, verbose_name="Наименование")
    description = BBCodeTextField(null=True, blank=True,verbose_name='Описание')
    deadline = models.DateField(db_index=True, verbose_name="Срок исполнения")
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата публикации")
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.not_started, verbose_name="Статус")
    done_date = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="Дата исполнения")
    time_to_do = DateTimeRangeField(verbose_name='Время на выполнение', null=True)
    time_allotted = models.DurationField(verbose_name='Отведенное время', null=True, blank=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name_plural = 'Задачи'
        verbose_name = 'Задача'

class Subscribes(models.Model):
    email = models.CharField(max_length=30, verbose_name="Mейл",unique=True)

card_number_validator = RegexValidator(
    regex=r'^\d{16}$',
    message="Номер карты должен состоять ровно из 16 цифр."
)

class Sub_info(models.Model):
    COUNTRY_CHOICES = [
        ('RU', 'Россия'),
        ('US', 'США'),
        ('GB', 'Великобритания'),
        ('GR', 'Греция'),
    ]
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, verbose_name="Страна")
    address = models.CharField(max_length=200, verbose_name="Адрес проживания")
    card_num = models.CharField(max_length=16, verbose_name="Номер карты", validators=[card_number_validator])
    acc_num = IBANField(include_countries=('RU', 'GB', 'GR'))
    bic = BICField()
    mail = models.OneToOneField(Subscribes, on_delete=models.CASCADE, verbose_name="электронный адрес",
                                related_name="subscriber_email")

class Icecream(models.Model):

    class Package(models.TextChoices):
        Cup = 'cup', 'стаканчик'
        Cone = 'cone', 'рожок'
        Brick = 'brick', 'брикет'
        Tube = 'tube', 'туба '
        Box = 'box', 'коробка'
        Pouch = 'pouch', 'пакетик'
        Foil = 'foil', 'фольга'
        Plastic_container = 'plastic_container', 'пластиковый контенер'
        Paper_container = 'paper container', 'бумажный контенер'
        Balls = 'balls', 'шарик'

    name = models.CharField(max_length=40, verbose_name="Тороговое наименование")
    fabricator = models.CharField(max_length=40, verbose_name="Производитель")
    composition = models.CharField(max_length=500, verbose_name="Состав", null=True, blank=True)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Стоимость")
    package = models.CharField(max_length=20, choices=Package.choices, default=Package.Balls, verbose_name="Упаковка")
    weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Вес нетто", default=200.00)
    expiration_date_in_days = models.IntegerField(verbose_name="Срок употребления", default=30)

    class Meta:
        verbose_name_plural = 'Мороженое'
        verbose_name = 'Мороженое'
        ordering = ['name']
        abstract = True

    def __str__(self):
        return self.name

class SpecialIcecream(Icecream):
    vegan = models.BooleanField(default=False, verbose_name="Веганское")
    sugar_free = models.BooleanField(default=False, verbose_name="Без добавления сахара")

    class Meta:
        verbose_name_plural = 'Специальное мороженое'
        verbose_name = 'Специальное мороженое'
        abstract = True

class LimitedEditionIcecream(SpecialIcecream):
    theme = models.CharField(max_length=50, verbose_name="Тематика", blank=True, null=True)
    season = models.CharField(max_length=50, verbose_name="Сезон/Праздник", blank=True, null=True)
    sale_start_date = models.DateField(verbose_name="Дата начала продаж", blank=True, null=True)
    sale_end_date = models.DateField(verbose_name="Дата окончания продаж", blank=True, null=True)
    unique_flavors = models.TextField(verbose_name="Уникальные вкусы",
                                      help_text="Перечислите уникальные вкусы этой серии", blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Ограниченная серия мороженого'
        verbose_name = 'Ограниченная серия мороженого'

    def __str__(self):
        return f"{self.theme} - {self.season}"

class Vendors(models.Model):
    name = models.CharField(max_length=40, verbose_name="Наименование продавца")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    number = models.CharField(max_length=200, verbose_name="Номер для связи", blank=True, null=True)
    icecream_pl = models.ManyToManyField(LimitedEditionIcecream, through='Vendors_Icecream', through_fields=('vendor',
                                                                                               'icecream_position'))
    class Meta:
        verbose_name_plural = 'Продавцы'
        verbose_name = 'Продавец'
        ordering = ['name']

    def __str__(self):
        return self.name

class Vendors_Icecream(models.Model):
    icecream_position = models.ForeignKey(LimitedEditionIcecream, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

class PassValidator():
    def __init__(self, password):
        self.password = password
    def check_item(self):
        upper_count = 0
        lower_count = 0
        digit_count = 0
        spec_signs_count = 0
        signs = ["!", "@", "#", "$", "%", "^", "&", "*", "-", "+", "/"]
        for letter in self.password:
            if letter.isupper():
                upper_count += 1
            elif letter.islower():
                lower_count += 1
            elif letter.isdigit():
                digit_count += 1
            elif letter in signs:
                spec_signs_count += 1
        if upper_count > 0 and lower_count > 0 and digit_count > 0 and spec_signs_count > 0:
            return True

    def __call__(self, value):
        if len(value) < 6 or not self.check_item():
            raise ValidationError('Пароль должен содержать не менее 6 символов и не менее одной прописной буквы, строчной буквы, цифры и специального знака',
                                  code='out_of_range', params={'password': value})



class LogModel(models.Model):
    time = models.DateTimeField()
    levelname = models.CharField(max_length=15)
    levelnum = models.PositiveIntegerField()
    pathname = models.CharField(max_length=1024)
    line = models.PositiveIntegerField()
    message = models.TextField()

    def __str__(self):
        return f'{self.level_title}'




