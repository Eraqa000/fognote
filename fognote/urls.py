from django.contrib import admin
from django.urls import path
from notes.views import (
    home, note_list,
    register_view, login_view, logout_view,
    create_note, edit_note, delete_note, profile_view, edit_profile,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("notes/", note_list, name="note_list"),

    path("notes/add/", create_note, name="create_note"),
    path("notes/<int:note_id>/edit/", edit_note, name="edit_note"),
    path("notes/<int:note_id>/delete/", delete_note, name="delete_note"),

    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),


]