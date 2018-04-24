import random, time
from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.permissions import IsOwnerOrReadOnly
from utils.alipay import AliPay
from .serializers import ShopCartSerializer,ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods
from mxshop.settings import appid, private_key_path, alipay_pub_key_path, alipay_notify_url, alipay_return_url
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
    

class AliPayViewset(APIView):
    def get(self, request):
        """
        处理支付宝return_url 返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value
        
        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            appid=appid,
            app_notify_url=alipay_notify_url,
            app_private_key_path=private_key_path,
            alipay_public_key_path=alipay_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=alipay_return_url,
        )
        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
        #     order_sn = processed_dict.get('out_trade_no', None)
        #     trade_no = processed_dict.get('trade_no', None)
        #     trade_status = processed_dict.get('trade_status', None)
            
        #     existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
        #     for existed_order in existed_orders:
        #         existed_order.pay_status = trade_status
        #         existed_order.trade_no = trade_no
        #         existed_order.pay_time = datetime.now()
        #         existed_order.save()

            return Response("success")


    def post(self, request):
        """
        处理支付宝notify_url 返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value
            print(key, value)
        
        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            appid=appid,
            app_notify_url=alipay_notify_url,
            app_private_key_path=private_key_path,
            alipay_public_key_path=alipay_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=alipay_return_url,
        )
        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)
            
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return Response("success")