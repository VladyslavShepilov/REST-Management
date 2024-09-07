from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrOrganizerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.organizer == request.user or request.user.is_staff
