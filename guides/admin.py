from django.contrib import admin
from .models import Company, Game, Achievement, Guide, AchievementType, Genre

# --- 1. STORY ---
@admin.action(description='Mark selected as Story')
def mark_as_story(modeladmin, request, queryset):
    story_type, created = AchievementType.objects.get_or_create(name='Story')
    for ach in queryset:
        ach.type.add(story_type)
    modeladmin.message_user(request, f'Vybraným achievementům byl přidán typ Story.')

# --- 2. MISSABLE ---
@admin.action(description='Mark selected as Missable')
def mark_as_missable(modeladmin, request, queryset):
    # Opraveno: použití get_or_create a add() místo upadte()
    missable_type, created = AchievementType.objects.get_or_create(name='Missable')
    for ach in queryset:
        ach.type.add(missable_type)
    modeladmin.message_user(request, f'Vybraným achievementům byl přidán typ Missable.')

# --- 3. MULTIPLAYER ---
@admin.action(description='Mark selected as Multiplayer')
def mark_as_multiplayer(modeladmin, request, queryset):
    multiplayer_type, created = AchievementType.objects.get_or_create(name='Multiplayer')
    for ach in queryset:
        ach.type.add(multiplayer_type)
    modeladmin.message_user(request, f'Vybraným achievementům byl přidán typ Multiplayer.')

# --- 4. COLLECTIBLE ---
@admin.action(description='Mark selected as Collectible')
def mark_as_collectible(modeladmin, request, queryset):
    collectible_type, created = AchievementType.objects.get_or_create(name='Collectible')
    for ach in queryset:
        ach.type.add(collectible_type)
    modeladmin.message_user(request, f'Vybraným achievementům byl přidán typ Collectible.')

@admin.action(description='Remove type Collectible')
def remove_collectible(modeladmin, request, queryset):
    # Najdeme typ Story (použijeme .first(), aby to nespadlo, pokud by v databázi náhodou nebyl)
    collectible_type = AchievementType.objects.filter(name='Collectible').first()
    
    if collectible_type:
        for ach in queryset:
            ach.type.remove(collectible_type) # Zde používáme .remove()
        
        modeladmin.message_user(request, 'Typ Collectible byl úspěšně odebrán.')
    else:
        modeladmin.message_user(request, 'Typ Collectible v databázi neexistuje.', level='error')

# --- 5. QUEST ---
@admin.action(description='Mark selected as Quest')
def mark_as_quest(modeladmin, request, queryset):
    quest_type, created = AchievementType.objects.get_or_create(name='Quest')
    for ach in queryset:
        ach.type.add(quest_type)
    modeladmin.message_user(request, f'Vybraným achievementům byl přidán typ Quest.')

admin.site.register(AchievementType)
admin.site.register(Guide)
admin.site.register(Genre)
admin.site.register(Company)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'get_types','description' ) 
    list_filter = ('type', 'game')
    search_fields = ('title',)
    
    # Zde jsme přidali všechny vytvořené funkce do seznamu
    actions = [mark_as_story, mark_as_missable, mark_as_multiplayer, mark_as_collectible, mark_as_quest, remove_collectible]

    def get_types(self, obj):
        return ", ".join([t.name for t in obj.type.all()])
    get_types.short_description = 'Types'

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_genres', 'release_year','get_developers','get_publishers', 'total_achievements' ) 
    list_filter = ('genres','developers','publishers', 'release_year' )
    search_fields = ('name',)

    def get_genres(self, obj):
        return ", ".join([g.name for g in obj.genres.all()])
    get_genres.short_description = 'Genres'

    def get_developers(self, obj):
        return ", ".join([d.name for d in obj.developers.all()])
    get_developers.short_description = 'Developers'

    def get_publishers(self, obj):
        return ", ".join([p.name for p in obj.publishers.all()])
    get_publishers.short_description = 'Publishers'