from django.db import models
from django.utils.text import slugify

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

class Game(models.Model):
    name = models.CharField(max_length=200)
    steam_appid = models.IntegerField(unique=True)
    genres = models.ManyToManyField(Genre, related_name="games", blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    developers = models.ManyToManyField(
        Company,
        related_name="developed_games",
        blank=True
    )

    publishers = models.ManyToManyField(
        Company,
        related_name="published_games",
        blank=True
    )

    total_achievements = models.IntegerField(default=0)
    theme = models.CharField(max_length=50, default="default")
    slug = models.SlugField(unique=True, blank=True)
    cover_url = models.URLField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AchievementType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Achievement(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="achievements")
    api_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.URLField(blank=True, null=True)
    type = models.ManyToManyField(AchievementType, related_name="achievements", blank=True)
    
    # NOVÉ POLE:
    slug = models.SlugField(max_length=255, blank=True)

    # NOVÁ METODA: Automatické vytvoření slugu při uložení
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.game.name} - {self.title}"

class Guide(models.Model):
    achievement = models.OneToOneField(Achievement, on_delete=models.CASCADE)
    guide_text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard")
    ])

    def __str__(self):
        return f"Guide: {self.achievement.title}"