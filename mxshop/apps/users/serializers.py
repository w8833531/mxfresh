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
from rest_framework.validators import UniqueValidator

from .models import VerifyCode, UserProfile
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


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册
    """
    # code 为UserProfile模块中不存在的列(属性)，会在下面的validate函数中删除
    # error_messages为自定义报错信息
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4,
                                 error_messages={
                                     "required": "请输入验证码",
                                     "max_length": "验证码大于4位",
                                     "min_length": "验证码小于4位",
                                 },
                                 label="验证码")
    username = serializers.CharField(required=True, allow_blank=False, label="用户名", validators=[
                                     UniqueValidator(queryset=User.objects.all(), message="用户名已经存在")])
    password = serializers.CharField(
        style={'input_type': 'password'}, label="密码", write_only=True)

    # 重载ModelSerializer.create 方法, 使用UserProfile.set_password方法来加密password并保存
    # 但建议使用django的Model signals 来解决这类问题，在做model save时来处理
    # def create(self, validated_data):
    #     user = super(UserRegSerializer, self,).create(validated_data=validated_data)
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user

    def validate_code(self, code):
        verify_records = VerifyCode.objects.filter(
            mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]
            # 这里使用了datetime.utcnow()和 last_record.add_time.replace(tzinfo=None) 把两个时间统一成 UTC native time进行比较
            five_minute_ago = datetime.utcnow() - timedelta(hours=0, minutes=5, seconds=0)
            if five_minute_ago > last_record.add_time.replace(tzinfo=None):
                raise serializers.ValidationError("验证码过期")
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    # 通过属性(attrs--对应表中的列)把UserProfile model（users_userprofile表）中的mobile 设置成和 username值相同，去掉多增加的code，并返回
    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")
