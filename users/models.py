# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from guides.models import Achievement
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

class CustomUser(AbstractUser):
    steam_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    steam_name = models.CharField(max_length=150, blank=True, null=True) # 👈 NOVÉ POLE pro přezdívku ze Steamu
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

class UserAchievement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="unlocked_achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

# Signál pro propojení přes nastavení / stávající účet
@receiver(social_account_added)
def populate_profile_on_connect(request, sociallogin, **kwargs):
    user = sociallogin.user
    
    if sociallogin.account.provider == 'steam':
        user.steam_id = sociallogin.account.uid
        
        extra_data = sociallogin.account.extra_data
        if 'avatarfull' in extra_data:
            user.avatar_url = extra_data['avatarfull']
        if 'personaname' in extra_data: # 👈 Uložení přezdívky ze Steamu
            user.steam_name = extra_data['personaname']
            
        user.save()

# Signál pro registraci nového účtu napřímo přes Steam
@receiver(user_signed_up)
def populate_user_profile(request, user, **kwargs):
    if user.socialaccount_set.filter(provider='steam').exists():
        steam_account = user.socialaccount_set.get(provider='steam')
        user.steam_id = steam_account.uid
        
        extra_data = steam_account.extra_data
        if 'avatarfull' in extra_data:
            user.avatar_url = extra_data['avatarfull']
        if 'personaname' in extra_data: # 👈 Uložení přezdívky ze Steamu
            user.steam_name = extra_data['personaname']
            
        user.save()