#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# serializers.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 3/27/2018, 3:57:48 PM
from rest_framework import serializers
from .models import Goods, GoodsCategory

class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Goods
        fields = "__all__"


