from rest_framework.permissions import BasePermission, SAFE_METHODS

"""用户管理同样涉及的权限问题，因此新建 permissions.py，写入代码："""
class IsSelfOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user