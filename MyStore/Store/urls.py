
from django.urls import path,re_path
from Store.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    re_path('^$',login),
    path('bt/',button),
    path('rs/',register_store),
    path('ag/',add_goods),
    path('gl/',goods_list),
    re_path(r'^goods/(?P<goods_id>\d+)',goods),
    re_path(r'update_goods/(?P<goods_id>\d+)',update_goods),

]
urlpatterns += [
    path('base/',base)
]