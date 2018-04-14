from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from .models import UserFav
from .serializer import UserFavSerializer
from utils.permissions import IsOwnerOrReadOnly

# Create your views here.

class UserFavViewset(mixins.CreateModelMixin,mixins.ListModelMixin, mixins.DestroyModelMixin,mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户收藏功能
    """
    # 设置当前用户要登录且只能访问本用户的数据
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    serializer_class = UserFavSerializer
    # 设置要求使用JWT认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 设置queryset 为当前用户的数据
    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)