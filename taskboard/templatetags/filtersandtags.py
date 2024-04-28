from django import template
from django.utils.safestring import mark_safe
register = template.Library()
@register.filter
def transliterate(text):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '',
        'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    transliterated_text = ''.join(translit_dict.get(char, char) for char in text)
    return transliterated_text

@register.filter
def stat_color(percentage):
    percent_value = float(percentage.split(' ')[0])

    if percent_value < 40:
        return mark_safe(f'<span style="color: red;">{percentage}</span>')
    elif 40 <= percent_value <= 80:
        return mark_safe(f'<span style="color: orange;">{percentage}</span>')
    elif percent_value > 80:
        return mark_safe(f'<span style="color: green;">{percentage}</span>')
    return mark_safe(f'<span style="color: green;">Не понятно</span>')


@register.simple_tag
def statistic(common_count, count):
    if common_count == 0:
        return f'{100} %'
    else:
        percent = count/common_count*100
        return f'{percent} %'

@register.simple_tag
def format_task_status(status):
    print(status)
    if status in ['n', 'p']:
        return mark_safe('<span style="color: red;">Не завершено</span>')
    elif status == 'd':
        return mark_safe('<span style="color: green;">Завершено</span>')
    return mark_safe('<span>Статус не определён</span>')