from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Note(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes",
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    title = models.CharField("Заголовок", max_length=200)
    body = models.TextField("Текст")
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField("О себе", blank=True, null=True)
    location = models.CharField("Локация", max_length=100, blank=True, null=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    theme = models.CharField("Тема", max_length=10, default="light")  # на будущее
    avatar = models.URLField("Аватар", blank=True, null=True)  # <— ДОБАВИЛИ

    def __str__(self):
        return f"Профиль {self.user.username}"



# Автосоздание профиля после регистрации пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)