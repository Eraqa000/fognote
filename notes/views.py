from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import NoteForm
from django.shortcuts import get_object_or_404
from .models import Note, Profile
from django.contrib.auth.decorators import login_required
from django import forms
from .supabase_client import supabase
import uuid


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "location"]  # avatar УБРАЛИ из списка полей
        widgets = {
            "bio": forms.Textarea(attrs={"class": "input", "rows": 3}),
            "location": forms.TextInput(attrs={"class": "input"}),
        }





@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():

            avatar_file = request.FILES.get("avatar")

            if avatar_file:
                # генерируем имя файла
                file_ext = avatar_file.name.split(".")[-1]
                unique_name = f"{request.user.username}_{uuid.uuid4()}.{file_ext}"

                # загружаем в Supabase Storage
                supabase.storage \
                    .from_("avatars") \
                    .upload(unique_name, avatar_file.read())

                # получаем публичный url
                public_url = supabase.storage \
                    .from_("avatars") \
                    .get_public_url(unique_name)

                profile.avatar = public_url

            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "notes/edit_profile.html", {"form": form})


def home(request):
    return render(request, "notes/home.html")

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, "notes/profile.html", {"profile": profile})



@login_required
def create_note(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user     # привязываем заметку к пользователю
            note.save()
            return redirect("note_list")
    else:
        form = NoteForm()

    return render(request, "notes/create_note.html", {
        "profile": profile,
        "form": form,
    })



@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm(instance=note)

    return render(request, "notes/edit_note.html", {
        "profile": profile,
        "form": form,
    })


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.delete()
    return redirect("note_list")


@login_required
def note_list(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    notes = Note.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notes/note_list.html", {
        "notes": notes,
        "profile": profile,
    })



def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # сразу логиним после регистрации
            return redirect("note_list")
    else:
        form = UserCreationForm()

    return render(request, "notes/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # если был параметр ?next=/что-то/, Django сам туда отправит
            if user.is_superuser:
                return redirect("/admin/")
            return redirect(request.GET.get("next") or "note_list")

    else:
        form = AuthenticationForm()

    return render(request, "notes/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
