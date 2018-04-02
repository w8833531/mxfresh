#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# filters.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/2/2018, 11:10:09 AM
from rest_framework import generics
from django_filters import rest_framework as filters
from .models import Goods


class GoodsFilter(filters.FilterSet):
    """
    商品过滤类
    """
    price_min = filters.NumberFilter(name="shop_price", lookup_expr='gte')
    price_max = filters.NumberFilter(name="shop_price", lookup_expr='lte')

    class Meta:
        model = Goods
        fields = ['name', 'shop_price']