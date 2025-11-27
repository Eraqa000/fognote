from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Note, Profile
from .admin_dashboard import fognote_admin


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0
    verbose_name = "Профиль"
    verbose_name_plural = "Профиль пользователя"
    can_delete = False


class CustomUserAdmin(UserAdmin):
    """Кастомная страница изменения пользователя в админке."""

    inlines = [ProfileInline]

    # колонки в списке пользователей
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "notes_count",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "first_name", "last_name", "email")

    # поля только для чтения
    readonly_fields = ("password", "last_login", "date_joined", "notes_count")

    # как выглядит страница изменения пользователя
    fieldsets = (
        ("Учетная запись", {
            "fields": ("username", "password"),
            "description": "Логин и хэш пароля (настоящий пароль увидеть нельзя).",
        }),
        ("Личные данные", {
            "fields": ("first_name", "last_name", "email"),
        }),
        ("Статус", {
            "fields": ("is_active", "is_staff", "is_superuser"),
        }),
        ("Группы и права", {
            "fields": ("groups", "user_permissions"),
        }),
        ("Активность и статистика", {
            "fields": ("last_login", "date_joined", "notes_count"),
            "description": "Информация о регистрации и активности пользователя.",
        }),
    )

    # как выглядит форма создания нового пользователя в админке
    add_fieldsets = (
        ("Создание пользователя", {
            "classes": ("wide",),
            "fields": (
                "username",
                "first_name",
                "last_name",
                "email",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    def notes_count(self, obj):
        return obj.notes.count()
    notes_count.short_description = "Заметок"


# регистрируем в нашем кастомном AdminSite
fognote_admin.register(User, CustomUserAdmin)
fognote_admin.register(Note)
fognote_admin.register(Profile)
