from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Game, Achievement, Guide
from users.models import UserAchievement
from .steam_api import import_steam_game, search_steam_game, sync_user_achievements


def games(request):
    games = Game.objects.all()
    return render(request, "games.html", {"games": games})

def achievement_detail(request, achievement_id):
    achievement = get_object_or_404(Achievement, id=achievement_id)
    return render(request, "achievement_detail.html", {"achievement": achievement})

def import_game(request, appid):
    hra = import_steam_game(appid)
    return HttpResponse(f"Hra {hra.name} byla úspěšně importována")

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    achievements = game.achievements.all()
    types = (achievements.values_list('type__name', flat=True)
    .distinct()
    )
    achievement_types = sorted(set(t for t in types if t))
    
    if request.user.is_authenticated and request.user.steam_id:
        # Zaktualizujeme data rovnou při načtení stránky!
        sync_user_achievements(request.user, game.steam_appid)
        
    unlocked_ids = []
    if request.user.is_authenticated:
        unlocked_ids = UserAchievement.objects.filter(
            user=request.user, 
            achievement__game=game
        ).values_list('achievement_id', flat=True)

    return render(request, "game_detail.html", {
        "game": game,
        "achievements": achievements,
        "achievement_types": achievement_types,
        'unlocked_ids': unlocked_ids
    })

def steam_search(request):
    dotaz = request.GET.get("q")
    vysledky = []

    if dotaz:
        vysledky = search_steam_game(dotaz)

    return render(request, "search.html", {
        "dotaz": dotaz,
        "vysledky": vysledky
    })
