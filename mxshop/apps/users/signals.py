#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# signals.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/11/2018, 2:56:47 PM
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

@receiver(post_save, sender=User)
def create_user(sender, instance=None, created=False, **kwargs):
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()