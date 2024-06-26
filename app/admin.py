from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Task


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "phone", "type", "photo")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "type",
                    "photo",
                ),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "last_name", "type", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "employee",
        "status",
        "created_at",
        "updated_at",
        "closed_at",
    )
    list_filter = ("status", "created_at", "updated_at", "closed_at")
    search_fields = ("client__username", "employee__username", "status")


admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
