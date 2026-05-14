from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("games/", views.games, name="games"),
    path("achievement/<int:achievement_id>/", views.achievement_detail, name="achievement_detail"),
    path("import/<int:appid>/", views.import_game, name="import_game"),
    path("api/steam-search/", views.steam_search),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("search/", views.steam_search, name="steam_search"),
    path("<slug:slug>/", views.game_detail, name="game_detail"),
]