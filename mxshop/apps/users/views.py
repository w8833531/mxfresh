import re, uuid, json
from datetime import datetime, timedelta
from random import choice
from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.utils import jwt_encode_handler


from .serializers import SmsSerializer, UserRegSerializer
from .models import VerifyCode
from utils import sms_send
# Create your views here.
User = get_user_model()

class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self, username=None, password=None, **Kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
            else:
                return None
        except Exception as e:
            return None


class SmsCodeViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # send sms
        mobile = serializer.validated_data["mobile"]
        __business_id = uuid.uuid1()
        code = get_random_string(length=4, allowed_chars='0123456789')
        params = "{\"code\":\"" + code + "\"}"
        sms_status=sms_send.send_sms(__business_id, mobile, "鹰之家", "SMS_130930043", params)
        sms_status=json.loads(sms_status)
        if sms_status["Code"] != "OK":
            return Response({
                "mobile": sms_status["Message"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


class UserViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    用户注册
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        """
        重载create 方法，在返回数据serializer.data中增加username 和 token,让注册完的用户马上就可以实现登录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        # 通过 rest_framework_jwt.utils 两个方法先通过user 获取payload,再通过payload获取token,通过re_dict 返回
        re_dict = serializer.data       
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()