#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sentry_test.py
# @Author : 吴鹰 (wuying)
# @Link   : 
# @Date   : 5/9/2018, 5:08:31 PM

dsn = "http://59369be85a0f43aead58fa54a3ffeb69:2a8220d6706f48d48973a8b5692130e6@127.0.0.1:9000/3"
from raven import Client

client = Client(dsn)

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()
