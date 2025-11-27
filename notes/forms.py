from django import forms
from .models import Note
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя", max_length=50)
    last_name = forms.CharField(label="Фамилия", max_length=50)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Телефон", max_length=20)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Логин должен быть на английском и содержать только буквы, цифры и _")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Такой логин уже используется")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Такой email уже зарегистрирован")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]

        if len(password) < 8:
            raise ValidationError("Пароль должен быть не меньше 8 символов")

        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("Пароль должен содержать буквы")

        if not re.search(r'[0-9]', password):
            raise ValidationError("Пароль должен содержать цифры")

        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError("Пароль должен содержать символы")

        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают")

        return cleaned



class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "input",
                "placeholder": "Заголовок"
            }),
            "body": forms.Textarea(attrs={
                "class": "textarea",
                "placeholder": "Текст заметки..."
            }),
        }
