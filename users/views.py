from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def user_profile(request):
    user = request.user
    
    # Allauth ukládá propojení do modelu SocialAccount. 
    # Můžeme zjistit, jaké sítě má uživatel aktuálně propojené.
    social_accounts = user.socialaccount_set.all()
    
    # Pro snazší podmínky v šabloně si připravíme booleany
    providers = [account.provider for account in social_accounts]
    has_steam = 'steam' in providers
    has_xbox = 'xbox' in providers  # Příprava do budoucna
    has_psn = 'playstation' in providers  # Příprava do budoucna

    context = {
        'user': user,
        'has_steam': has_steam,
        'has_xbox': has_xbox,
        'has_psn': has_psn,
        # Můžeš sem přidat i další statistiky, např. počet odemčených achievementů
        'unlocked_count': user.unlocked_achievements.count()
    }
    
    return render(request, "profile.html", context)