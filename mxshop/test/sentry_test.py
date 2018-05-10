#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sentry_test.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 5/9/2018, 5:08:31 PM

dsn = "http://ea848a57fe8a46be9938677eba633f1d:6aa3b185b8884199be148b8081d3d9f6@techdevops:9000/3"
from raven import Client

client = Client(dsn)

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()
