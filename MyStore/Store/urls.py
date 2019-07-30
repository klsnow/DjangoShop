
from django.urls import path,re_path
from Store.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    re_path('^$',login),
    path('rs/',register_store),
    path('ag/',add_goods),
    re_path('gl/(?P<state>\w+)/',goods_list),
    re_path(r'^goods/(?P<goods_id>\d+)',goods),
    re_path(r'update_goods/(?P<goods_id>\d+)',update_goods),
    re_path(r'set_goods/(?P<state>\w+)/',set_goods),
    path('logout/',logout),
    path('ags/',add_goods_style),
    path('gsl/',goods_style_list),
    path('ol/',order_list),

]
urlpatterns += [
    path('base/',base)
]