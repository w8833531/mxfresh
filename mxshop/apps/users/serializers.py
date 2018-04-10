#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# serializers.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/9/2018, 4:22:05 PM
import re
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import VerifyCode
from mxshop.settings import REGEX_MOBILE

User = get_user_model()

class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    def validate_mobile(self, mobile):
        """
        验证手机号
        """
        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")
        # 手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")
        # 发送频率
        one_minute_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minute_ago, mobile=mobile):
            raise serializers.ValidationError("离上次发送小于60秒")

        return mobile