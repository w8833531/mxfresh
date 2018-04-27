#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# signals.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/11/2018, 2:56:47 PM
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from user_operation.models import UserFav

User = get_user_model()


@receiver(post_save, sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    if created:
        # when user add fav , goods.fav_num + 1
        goods = instance.goods
        goods.fav_num += 1
        goods.save()

@receiver(post_delete, sender=UserFav)
def delete_userfav(sender, instance=None, created=False, **kwargs):
        # when user add fav , goods.fav_num + 1
        goods = instance.goods
        if goods.fav_num > 0:
            goods.fav_num -= 1 
        goods.save()