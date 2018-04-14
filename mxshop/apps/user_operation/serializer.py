#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# serializer.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/14/2018, 8:29:11 PM

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator 

from .models import UserFav


class UserFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏"
            )
        ]
        fields = ("id", "user", "goods")
