import re, uuid, json
from datetime import datetime, timedelta
from random import choice
from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.utils import jwt_encode_handler


from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
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
    create:
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


class UserViewset(CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    create:
        用户注册
    read:
        获取某个用户信息
    update:
        更新用户信息
    
    """
    
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication )
    # permission_classes = (permissions.IsAuthenticated)
    # 重载get_permissions方法，在用户注册(create)时不用登录，其它方式如(retrieve)要求登录,注意返回permissions.IsAuthenticated()实例 
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
           return []
        return [] 
    # serializer_class = UserRegSerializer
    # 重载 get_serializer_class方法，在用户注册时用UserRegSerializer， 其它方式用UserDetailSerializer
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
           return UserRegSerializer
        return UserDetailSerializer 

    def create(self, request, *args, **kwargs):
        """   
            用户注册
        """
        # 重载create 方法，在返回数据serializer.data中增加username 和 token,让注册完的用户马上就可以实现登录
        
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
    # 重载 mixins.RetrieveModelMixin的get_object 方法，返回当前用户对象
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()