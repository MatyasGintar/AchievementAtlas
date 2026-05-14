import requests
from django.conf import settings
from .models import Game, Achievement, Company, Genre
from users.models import UserAchievement

def get_game_achievements(appid):
    url = "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
    params = {
        "key": settings.STEAM_API_KEY,
        "appid": appid,
        "l": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except:
        return []

    game = data.get("game", {})
    stats = game.get("availableGameStats", {})

    if not stats:
        return []

    achievements = stats.get("achievements")
    if not achievements:
        return []

    return achievements


def import_steam_game(appid):
    details = get_game_details(appid)
    if not details:
        return None

    # Vytvoření nebo získání hry (Bez ManyToMany polí, ta se přidávají až po uložení)
    game, created = Game.objects.get_or_create(
        steam_appid=appid,
        defaults={
            "name": details["name"],
            "release_year": details["release_year"],
            "cover_url": details["cover"],
            "banner_url": details["background"],
        }
    )

    # Aktualizace existující hry (pokud už v databázi byla)
    if not created:
        game.name = details["name"]
        game.release_year = details["release_year"]
        game.cover_url = details["cover"]
        game.banner_url = details["background"]
        game.save()

    # --- UKLÁDÁNÍ MANY-TO-MANY VAZEB ---
    # Nejprve je vyčistíme (pro případ, že děláš update existující hry)
    game.developers.clear()
    game.publishers.clear()
    game.genres.clear()

    # 1. Vývojáři
    for dev_name in details["developers"]:
        company, _ = Company.objects.get_or_create(name=dev_name)
        game.developers.add(company)

    # 2. Vydavatelé
    for pub_name in details["publishers"]:
        company, _ = Company.objects.get_or_create(name=pub_name)
        game.publishers.add(company)

    # 3. Žánry
    for genre_name in details["genres"]:
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        game.genres.add(genre)

    # --- UKLÁDÁNÍ ACHIEVEMENTŮ ---
    achievements = get_game_achievements(appid)
    
    # NOVÉ: Spočítáme stáhnuté achievementy a uložíme číslo do modelu Game
    game.total_achievements = len(achievements)
    game.save()

    for ach in achievements:
        Achievement.objects.get_or_create(
            game=game,
            api_name=ach["name"],
            defaults={
                "title": ach.get("displayName", ach["name"]),
                "description": ach.get("description", ""),
                "icon": ach.get("icon", "")
            }
        )

    return game


def search_steam_game(query):
    url = "https://store.steampowered.com/api/storesearch/"
    params = {
        "term": query,
        "l": "en",
        "cc": "cz"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError):
        return []

    results = []
    for item in data.get("items", []):
        results.append({
            "name": item.get("name"),
            "appid": item.get("id"),
            "image": item.get("tiny_image")
        })

    return results


def get_game_details(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=en"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except:
        return None

    game_data = data.get(str(appid), {}).get("data")
    if not game_data:
        return None

    # Získání VŠECH vývojářů a vydavatelů (Steam API je vrací jako seznam textů)
    developers = game_data.get("developers", [])
    publishers = game_data.get("publishers", [])

    # Získání PRVNÍCH TŘÍ žánrů (Steam API vrací žánry jako seznam slovníků)
    genres_raw = game_data.get("genres", [])
    genres = [g["description"] for g in genres_raw][:3]

    # Release year
    release_date = game_data.get("release_date", {}).get("date")
    release_year = None
    if release_date:
        try:
            release_year = int(release_date.strip()[-4:])
        except:
            pass

    return {
        "name": game_data.get("name"),
        "developers": developers,
        "publishers": publishers,
        "genres": genres,
        "release_year": release_year,
        "cover": game_data.get("header_image"),
        "background": game_data.get("background_raw"),
    }

def sync_user_achievements(user, appid):
    """
    Stáhne ze Steamu progres konkrétního hráče v konkrétní hře a uloží ho.
    Vrátí True, pokud se to povedlo, jinak False.
    """
    # Pokud uživatel nemá propojený Steam, nemáme co stahovat
    if not user.steam_id:
        return False

    url = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        "key": settings.STEAM_API_KEY,
        "steamid": user.steam_id,
        "appid": appid,
        "l": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Chyba při komunikaci se Steamem: {e}")
        return False

    # Steam vrací data v bloku "playerstats"
    stats = data.get("playerstats", {})
    
    # ⚠️ DŮLEŽITÉ: Pokud má uživatel "Soukromý profil" na Steamu, API nám data nedá!
    if not stats.get("success"):
        print("Steam odmítl vydat data (pravděpodobně soukromý profil).")
        return False

    achievements_data = stats.get("achievements", [])
    if not achievements_data:
        return False

    # Najdeme hru v naší databázi, abychom hledali jen její achievementy
    try:
        game = Game.objects.get(steam_appid=appid)
    except Game.DoesNotExist:
        return False

    # Projdeme vše, co nám Steam poslal
    for ach in achievements_data:
        # Zajímá nás to jen v případě, že je hodnota "achieved" rovna 1
        if ach.get("achieved") == 1:
            api_name = ach.get("apiname")
            
            try:
                # Najdeme achievement v naší databázi podle api_name
                achievement_obj = Achievement.objects.get(game=game, api_name=api_name)
                
                # Uložíme propojení do tabulky (get_or_create zaručí, že se nevytvoří duplikát)
                UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement_obj
                )
            except Achievement.DoesNotExist:
                # Pokud hráč získal achievement, který z nějakého důvodu nemáme v databázi, přeskočíme ho
                continue

    return True