
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

]
urlpatterns += [
    path('base/',base)
]