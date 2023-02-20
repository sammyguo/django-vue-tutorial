from rest_framework.permissions import BasePermission, SAFE_METHODS

"""评论对用户身份的要求比文章的更松弛，非安全请求只需要是本人操作就可以了。
因此自定义一个所有人都可查看、仅本人可更改的权限：
进行非安全请求时，由于需要验证当前评论的作者和当前登录的用户是否为同一个人，
这里用到了 def has_object_permission(...) 这个钩子方法，方法参数中的 obj 即为评论模型的实例。
"""

# class IsOwnerOrReadOnly(BasePermission):
#     # 第一次写权限
#     message = 'You must be the owner to update.'
#
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#
#         return request.user.is_authenticated
#
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#
#         return obj.author == request.user


"""重写方法"""
class IsOwnerOrReadOnly(BasePermission):
    message = 'You must be the owner to update.'

    def safe_methods_or_owner(self, request, func):
        if request.method in SAFE_METHODS:
            return True

        return func()

    def has_permission(self, request, view):
        return self.safe_methods_or_owner(
            request,
            lambda: request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return self.safe_methods_or_owner(
            request,
            lambda: obj.author == request.user
        )