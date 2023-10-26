from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User  # Import the User model
from .models import Company, UserProfile

# Register your models here.
#from .models import *
#admin.site.register([Envoi, User, TblBureau])
admin.site.register([Company, UserProfile] )


# Create a custom admin class for the User model
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')

    def get_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Groups'  # Set a custom column header name

# Replace the default User admin with the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

