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
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from goods.views import GoodsListViewSet
from mxshop.settings import MEDIA_ROOT

# 配置 URL Router
router = DefaultRouter()
# 配置 商品列表页面 goods的URL
router.register(r'^goods/$', GoodsListViewSet)


goods_list = GoodsListViewSet.as_view({
    'get': 'list',
})



urlpatterns = [
    # 管理站点xadmin url
    url(r'^xadmin/', xadmin.site.urls),
    # 增加富文本 DjangoUedit url
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    # 配置media document_root
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    # 商品列表页面
    # url(r'^goods/$', goods_list, name="goods-list"),

    # 生成DRF(Django RESTful Framework) 文档 url 配置
    url(r'docs/', include_docs_urls(title="慕学生鲜")),

    # DRF api 登录认证 url 配置
    url(r'^api-auth/', include('rest_framework.urls'))
]
