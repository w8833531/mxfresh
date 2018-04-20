import random, time
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication
from rest_framework import mixins
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.permissions import IsOwnerOrReadOnly
from .serializers import ShopCartSerializer,ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods
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


class OrderViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理
    List:
        获取订单
    Delete:
        删除订单
    Create:
        新增订单
    Retrieve:
        获取订单详情
    """
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderSerializer
    
    # 生成订单号 当前时间+userid+random
    def generate_order_sn(self):
        random_int = random.Random()
        order_sn = "{time_str}{userid}{random_str}".format(time_str=time.strftime('%Y%m%d%H%M%S'),
                        userid=self.request.user.id, random_str=random_int.randint(10, 99))
        return order_sn

    # override perform_create method, set order_sn in serializer.data
    def perform_create(self, serializer):
        order = serializer.save(order_sn=self.generate_order_sn())

        # 获取当前用户购物车内所有商品，放入定单，并清空购物车
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()
            
            shop_cart.delete()
        return order
    