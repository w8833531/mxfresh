#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# serializer.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/18/2018, 10:36:15 AM
import random, time
from rest_framework import serializers
from goods.models import Goods
from .models import ShoppingCart, OrderGoods, OrderInfo
from goods.serializers import GoodsSerializer


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = ShoppingCart
        fields = "__all__"

class ShopCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label="商品数量", min_value=1, 
                            error_messages={
                                "min_value": "商品数量",
                                "required": "请选择购买数量"
                            },
                            help_text="商品数量",
                        )
    goods = serializers.PrimaryKeyRelatedField(
                        queryset=Goods.objects.all(),
                        required=True,
                        help_text="商品名称",
                        )
    # override create method, shopcart good num+1 or create good and return chopcart good record
    def create(self, validated_data):
        # user in the context
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]
        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed =ShoppingCart.objects.create(**validated_data)
        return existed

    # add a update method for save date
    def update(self, instance, validated_data):
        # 修改购物车商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = OrderGoods
        fields = "__all__"

class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    class Meta:
        model = OrderInfo
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    # 隐藏用户信息
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 只读订单状态/交易号/订单号
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    # alipay_url = serializers.SerializerMethodField(read_only=True)
    
    
    # override validate method , set order_sn attribute
    # def validate(self, attrs):
    #    attrs["order_sn"] = self.generate_order_sn()
    #    return attrs


    class Meta:
        model = OrderInfo
        fields = "__all__"


        

