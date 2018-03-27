#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# views_base.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 3/26/2018, 9:30:26 PM

import json
from django.shortcuts import render
from django.views.generic import View
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from goods.models import Goods


class GoodsListView(View):
    """
    通过django的view实现商品列表页
    """
    def get(self, request):
        goods = Goods.objects.all()[:10]
        json_data = serializers.serialize('json', goods)
        json_data = json.loads(json_data)
        return JsonResponse(json_data, safe=False)




