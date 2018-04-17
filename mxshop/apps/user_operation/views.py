from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from .models import UserFav
from .serializer import UserFavSerializer, UserFavDetailSerializer
from utils.permissions import IsOwnerOrReadOnly

# Create your views here.

class UserFavViewset(mixins.CreateModelMixin,mixins.ListModelMixin, mixins.DestroyModelMixin,mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取用户收藏列表
    retrieve:
        判断某个商品是否已经收藏
    create:
        收藏商品
    delete:
        去掉收藏商品
    """
    # 设置当前用户要登录且只能访问本用户的数据
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    # serializer_class = UserFavSerializer
    # 重载 get_serializer_class方法，使用动态Serializer
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
           return UserFavSerializer
        return UserFavSerializer
    # 设置要求使用JWT认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    
    # 设置urlid 为goods_id而不是默认的表的PK
    lookup_field = "goods_id"

    # 设置queryset 为当前用户的数据
    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)