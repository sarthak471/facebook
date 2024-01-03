from django.contrib import admin
from .models import Friendship

admin.site.register(Friendship)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Extend the existing UserAdmin class
class UserAdmin(BaseUserAdmin):
    # Add 'id' to the list_display to see it in the admin panel
    list_display = BaseUserAdmin.list_display + ('id',)

# Unregister the original User admin
admin.site.unregister(User)

# Register the new UserAdmin
admin.site.register(User, UserAdmin)