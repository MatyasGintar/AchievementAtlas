from django.contrib.auth.models import AbstractUser
from django.db import models
from guides.models import Achievement # Importujeme achievementy z druhé aplikace
from allauth.account.signals import user_signed_up
from django.dispatch import receiver

class CustomUser(AbstractUser):
    steam_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

class UserAchievement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="unlocked_achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement') # Jeden achievement můžeš mít odemčený jen jednou

@receiver(user_signed_up)
def populate_user_profile(request, user, **kwargs):
    # Tento kód se spustí pokaždé, když se na webu zaregistruje nový uživatel
    
    # Podíváme se, jestli se přihlásil přes nějakou sociální síť (Steam)
    if user.socialaccount_set.filter(provider='steam').exists():
        steam_account = user.socialaccount_set.get(provider='steam')
        
        # Steam ukládá své ID do pole 'uid'
        user.steam_id = steam_account.uid
        
        # V 'extra_data' jsou schované informace o profilu přímo ze Steamu
        extra_data = steam_account.extra_data
        if 'avatarfull' in extra_data:
            user.avatar_url = extra_data['avatarfull']
            
        # Nezapomeneme uživatele uložit
        user.save()