from datetime import timedelta

from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.urls import path
from django.utils import timezone

from notes.models import Note, Profile


class FognoteAdminSite(AdminSite):
    site_header = "Fognote Admin"
    site_title = "Панель управления Fognote"
    index_title = "Администрирование Fognote"

    # /admin/ → сразу на дашборд
    def index(self, request, extra_context=None):
        return redirect("admin:dashboard")

    def get_urls(self):
        default_urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(self.dashboard_view), name="dashboard"),
            path("users/", self.admin_view(self.users_view), name="users_list"),
        ]
        return custom_urls + default_urls

    def dashboard_view(self, request):
        now = timezone.now()
        today = now.date()
        last_7_days = today - timedelta(days=6)

        total_users = User.objects.count()
        total_notes = Note.objects.count()
        total_profiles = Profile.objects.count()

        users_today = User.objects.filter(date_joined__date=today).count()
        notes_today = Note.objects.filter(created_at__date=today).count()

        users_last_7 = User.objects.filter(date_joined__date__gte=last_7_days).count()
        notes_last_7 = Note.objects.filter(created_at__date__gte=last_7_days).count()

        top_authors = (
            Note.objects.values("user__username")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")[:5]
        )

        recent_users = User.objects.order_by("-date_joined")[:5]
        recent_notes = Note.objects.select_related("user").order_by("-created_at")[:5]

        recent_logs = (
            LogEntry.objects.select_related("user", "content_type")
            .order_by("-action_time")[:10]
        )

        context = {
            "total_users": total_users,
            "total_notes": total_notes,
            "total_profiles": total_profiles,
            "users_today": users_today,
            "notes_today": notes_today,
            "users_last_7": users_last_7,
            "notes_last_7": notes_last_7,
            "top_authors": top_authors,
            "recent_users": recent_users,
            "recent_notes": recent_notes,
            "recent_logs": recent_logs,
        }

        return render(request, "admin/dashboard.html", context)

    def users_view(self, request):
        """Страница 'Все пользователи' в нашем стиле."""
        search = request.GET.get("q", "").strip()

        qs = User.objects.all().order_by("-date_joined").annotate(
            notes_cnt=Count("notes")
        )

        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        paginator = Paginator(qs, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "search": search,
        }
        return render(request, "admin/users_list.html", context)


fognote_admin = FognoteAdminSite(name="admin")
