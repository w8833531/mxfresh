#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# serializers.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 3/27/2018, 3:57:48 PM
from rest_framework import serializers
from .models import Goods, GoodsCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"

class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Goods
        fields = "__all__"