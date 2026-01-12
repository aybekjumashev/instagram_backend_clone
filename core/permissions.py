from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Oqıwǵa (GET, HEAD, OPTIONS) hámmege ruxsat.
    Jazıwǵa (PUT, DELETE) tek obyekttiń avtorına ruxsat.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user