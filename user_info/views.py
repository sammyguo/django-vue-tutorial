from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from user_info.permissions import IsSelfOrReadOnly
from user_info.serializers import UserRegisterSerializer, UserDetailSerializer

# Create your views here.

"""注册用户的 POST 请求是允许所有人都可以操作的，但其他类型的请求（比如修改、删除）就必须是本人才行了，
因此可以覆写 def get_permissions(...) 定义不同情况下所允许的权限。 permission_classes 接受列表，
因此可以同时定义多个权限，权限之间是 and 关系。注意这里的 lookup_field 属性，和序列化器中对应起来。"""

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    lookup_field = 'username'

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly, IsSelfOrReadOnly]

        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def info(self, request, username=None):
        queryset = User.objects.get(username=username)
        serializer = UserDetailSerializer(queryset, many=False)
        return Response(serializer.data)

    @action(detail=False)
    def sorted(self, request):
        users = User.objects.all().order_by('-username')

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)