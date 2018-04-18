from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.permissions import IsOwnerOrReadOnly
from .serializers import ShopCartSerializer, ShopCartDetailSerializer
from .models import ShoppingCart
# Create your views here.
class ShoppingCartViewset(viewsets.ModelViewSet):
    """
        购物车功能
    list:
        获取购物车物品列表
    create:
        加入购物车物品
    delete:
        删除购物车物品
    update:
        更新购物车物品 
    """
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    
    lookup_field = "goods_id"
    # override get_serializer_class method, if list return DetailSerializer
    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)