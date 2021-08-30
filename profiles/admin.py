from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .forms import UserCreateForm, UserForm
from .models import Profile, Country, User


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_under_represented')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name', 'position', 'institution')
    search_fields = ('first_name','last_name', 'institution', 'email')


class CustomUserAdmin(UserAdmin):
    add_form = UserCreateForm
    form = UserForm
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password','username','name', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email','username')
    ordering = ('email','username')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Country, CountryAdmin)