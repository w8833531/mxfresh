"""mxshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import xadmin
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve

from goods.views_base import GoodsListView
from mxshop.settings import MEDIA_ROOT

urlpatterns = [
    # 管理站点xadmin url
    url(r'^xadmin/', xadmin.site.urls),
    # 增加富文本 DjangoUedit url
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    # 配置media document_root
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    # 商品列表页面
    url(r'goods/$', GoodsListView.as_view(), name="goods-list"),
]
