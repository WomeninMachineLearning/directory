from django.contrib import admin

# Register your models here.
from .models import Profile, Country


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_under_represented')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'institution')
    search_fields = ('name', 'institution', 'email')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Country, CountryAdmin)
