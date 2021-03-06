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
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from goods.views import GoodsListViewSet, CategoryViewSet, HotSearchsViewset, BannerViewset, IndexCategoryViewset
from users.views import SmsCodeViewSet, UserViewset
from trade.views import ShoppingCartViewset, OrderViewset, AliPayViewset
from user_operation.views import UserFavViewset, LeavingMessageViewset, AddressViewset 
from mxshop.settings import MEDIA_ROOT
from social_django import urls, views
from rest_social_auth import urls_jwt


# 配置 DRF URL Router
router = DefaultRouter()
# 配置 商品列表页面 goods的URL
router.register(r'goods', GoodsListViewSet, base_name="goods")
# 配置 商品分类列表页面 goodscategory的URL
router.register(r'categorys', CategoryViewSet, base_name="categorys")
# 热搜词
router.register(r'hotsearchs', HotSearchsViewset, base_name="hotsearchs")
# 配置 验证码的获取URL
router.register(r'codes', SmsCodeViewSet, base_name="codes")
# 配置 用户注册URL
router.register(r'users', UserViewset, base_name="users")
# 配置 用户收藏URL
router.register(r'userfavs', UserFavViewset, base_name='userfavs')
# 留言
router.register(r'messages', LeavingMessageViewset, base_name="messages")
# 收货地址
router.register(r'address', AddressViewset, base_name="address")
# 购物车
router.register(r'shopcarts', ShoppingCartViewset, base_name='shopcarts')
# 订单
router.register(r'orders', OrderViewset, base_name='orders')
# 轮播图
router.register(r'banners', BannerViewset, base_name="banners")
# 首页商品展示
router.register(r'indexgoods', IndexCategoryViewset, base_name='indexgoods')

urlpatterns = [
    # 管理站点xadmin url
    url(r'^xadmin/', xadmin.site.urls),
    # 增加富文本 DjangoUedit url
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    # 配置media document_root
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    # REST Framework DefaultRouter register URL
    url(r'^', include(router.urls)),

    # 生成DRF(Django RESTful Framework) 文档 url 配置
    url(r'docs/', include_docs_urls(title="慕学生鲜")),

    # DRF api 登录认证 url 配置
    url(r'^api-auth/', include('rest_framework.urls')),
    # Add  drf(jdango rest framework) token auth
    # url(r'^api-token-auth/', views.obtain_auth_token),
    # add jwt(json web token) auth
    url(r'^login/$', obtain_jwt_token),
    # add alipay return_url
    url(r'^alipay/return/', AliPayViewset.as_view(), name="alipay"),
    # 第三方登录URL
    url(r'^api/login/', include('rest_social_auth.urls_jwt')),
    url(r'^api/login/', include('rest_social_auth.urls_token')),
    url(r'^api/login/', include('rest_social_auth.urls_session')),
    url('', include('social_django.urls', namespace='social')),
]
