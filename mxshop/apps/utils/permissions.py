#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# permissions.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 4/14/2018, 9:38:50 PM
from rest_framework import permissions
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user