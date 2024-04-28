from django.contrib import admin
from .models import Tasks, Subscribes, Vendors, Vendors_Icecream, LimitedEditionIcecream
class IcecreamInline(admin.TabularInline):
    model = Vendors_Icecream
    extra = 1
    can_delete = False

@admin.register(LimitedEditionIcecream)
class IcecreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'fabricator', 'composition', 'price', 'package', 'weight', 'expiration_date_in_days')
    list_filter = ('fabricator', 'package')
    search_fields = ('name', 'fabricator', 'composition')
    list_display_links = ('name',)
    inlines = (IcecreamInline,)
    list_editable = ('package', 'price')



# admin.site.register(LimitedEditionIcecream)
admin.site.register(Vendors)