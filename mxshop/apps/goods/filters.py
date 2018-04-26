#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# filters.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/2/2018, 11:10:09 AM
from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Goods


class GoodsFilter(filters.FilterSet):
    """
    商品过滤类
    """
    pricemin = filters.NumberFilter(name="shop_price", lookup_expr='gte', help_text="最低价格")
    pricemax = filters.NumberFilter(name="shop_price", lookup_expr='lte', help_text="最高价格")
    top_category = filters.NumberFilter(method='top_category_filter', help_text="上层类别")
    
    # name = filters.CharFilter(name="name", lookup_expr="icontains")
    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax', 'is_hot', 'is_new']
