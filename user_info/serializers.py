from django.contrib.auth.models import User
from rest_framework import serializers


class UserDescSerializer(serializers.ModelSerializer):
    """于文章列表中引用的嵌套序列化器"""
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'last_login',
            'date_joined'
        ]


"""用户管理涉及到对密码的操作，因此新写一个序列化器，覆写 def create(...) 和 def update(...) 方法
一般来说，博客是只允许博主自己发表文章的，因此之前设计的接口就有点缺陷了，它没有返回用户的权限信息。不过没关系，改起来也容易。
增加返回当前用户是否为超级用户的信息"""

class UserRegisterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='username')

    class Meta:
        model = User
        fields = [
            'url',
            'id',
            'username',
            'password',
            'is_superuser'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser':{'read_only':True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


"""视图集除了默认的增删改查外，还可以有其他的自定义动作。为了测试，首先写一个信息更加丰富的用户序列化器：
"""
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'last_name',
            'first_name',
            'email',
            'last_login',
            'date_joined'
        ]