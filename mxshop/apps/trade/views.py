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

    # 在创建订单时，重载 perform_create 方法, set order_sn in serializer.data
    def perform_create(self, serializer):
        """
        在创建订单时，关联订单中的商品，消减商品库存，清空购物车
        """
        # 保存当前用户的订单
        order = serializer.save(order_sn=self.generate_order_sn())
        # 获取当前用户购物车内所有商品条目
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        # 把商品、商品数量放入定单，库存相应消减，并清空购物车
        for shop_cart in shop_carts:
            # 生成订单商品对象
            order_goods = OrderGoods()
            # 把商品、商品数量放入订单商品对象
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            # 对商品的库存相应消减
            order_goods.goods.goods_num -= order_goods.goods_num
            order_goods.goods.save()
            # 放入订单对象并保存
            order_goods.order = order
            order_goods.save()
            # 清空购物车
            shop_cart.delete()
        return order
    # 在删除订单时，重载 perform_destroy 方法，实现订单商品库存增加
    def perform_destroy(self, instance):
        if instance.pay_status != "TRADE_SUCCESS":
            # 在删除订单前，如果订单没有支付成功，增加这个订单中的所有商品对应数量的库存
            order_goods = OrderGoods.objects.filter(order=instance.id)
            for order_good in order_goods:
                order_good.goods.goods_num += order_good.goods_num
                order_good.goods.save()
        instance.delete()
    

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
                # 如果支付成功，把订单中所有商品售出数量做相应增加
                if existed_order.pay_status == "TRADE_SUCCESS":
                    order_goods = existed_order.goods.all()
                    for order_good in order_goods:
                        order_good.goods.sold_num += order_good.goods_num
                        order_good.goods.save()
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return Response("success")