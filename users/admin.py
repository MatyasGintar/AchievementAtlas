from django.contrib import admin
from .models import UserAchievement, CustomUser
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserAchievement)