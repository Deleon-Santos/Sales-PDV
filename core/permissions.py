from rest_framework.permissions import BasePermission
from .models import User


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            User.Role.ADMIN,
            User.Role.MANAGER,
        }


class IsCashierOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.CASHIER,
        }
