

from django.urls import path,re_path

from Buyer.views import *
urlpatterns = [
    path('base/',base),
    path('re/',register),
    path('login/',login),
    path('index/',index),
    path('loginout/',loginout),
    path('detail/',detail),
    path('gl/',goods_list),
    path('po/',place_order),
    path('cart/',cart),
    path('add_cart/',add_cart),

]