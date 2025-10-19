from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "role")
    list_filter = ("role", "is_active", "is_staff")
    readonly_fields = ("date_joined", "last_login")
    fieldsets = (
        (None, {"fields": ("username", "email", "password", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    ordering = ("-date_joined",)
