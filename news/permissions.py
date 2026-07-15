"""
Custom API permissions based on user role.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import CustomUser


class ArticleRolePermission(BasePermission):
    """
    API permission rules:

    - Readers can only view.
    - Journalists can create, view, update, and delete.
    - Editors can view, update, delete, and approve.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == "POST":
            return request.user.role == CustomUser.JOURNALIST

        return request.user.role in [
            CustomUser.EDITOR,
            CustomUser.JOURNALIST,
        ]

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.approved or request.user.role in [
                CustomUser.EDITOR,
                CustomUser.JOURNALIST,
            ]

        if request.user.role == CustomUser.EDITOR:
            return True

        if request.user.role == CustomUser.JOURNALIST:
            return obj.author == request.user

        return False


class NewsletterRolePermission(BasePermission):
    """
    Newsletter permissions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in [
            CustomUser.EDITOR,
            CustomUser.JOURNALIST,
        ]