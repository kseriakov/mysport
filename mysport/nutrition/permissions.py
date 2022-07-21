from rest_framework import permissions


# создаем пользовательское ограничение на редактирование и
# удаление записи её владельцем
class IsOwnerUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # метод GET и.т.д.
            return True

        return request.user == obj.user