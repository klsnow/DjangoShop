import hashlib
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect

from Buyer.models import *
from Store.views import setPassword
from Store.models import *

def base(request):
    return render(request,"buyer/base.html")
def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        buyer = Buyer()
        buyer.username = username
        buyer.password = setPassword(password)
        buyer.email = email
        buyer.save()
        return HttpResponseRedirect("/buyer/login/")
    return render(request,"buyer/register.html")
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)

                if web_password == user.password :
                    response = HttpResponseRedirect("/buyer/index/")

                    response.set_cookie("user_id",user.id)

                    response.set_cookie("username",user.username)

                    request.session["username"] = user.username
                    return response
    return render(request,"buyer/login.html")

def loginvalid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/buyer/login/")
    return inner

def index(request):
    result_list = []
    goods_type_list = GoodsType.objects.all()
    for goods_type in goods_type_list:
        goods_list = goods_type.goods_set.values()[:4]
        if goods_list:
            goodsType = {
                'id': goods_type.id,
                'name':goods_type.name,
                'description':goods_type.description,
                'picture': goods_type.picture,
                'goods_list':goods_list,
            }
    return render(request,"buyer/index.html",locals())

def loginout(request):
    response = HttpResponseRedirect("/buyer/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)
    del request.session["username"]
    return response

def detail(request):
    goods_id = request.GET.get("id")
    if goods_id:
        goods = Goods.objects.filter(id = goods_id).first()
        return render(request,"buyer/detail.html",locals())

    return HttpResponse("没有你要的商品")

def goods_list(request):
    goodslist = []
    type_id = request.GET.get("type_id")
    type_name = request.GET.get("type_name")
    goods_type = GoodsType.objects.filter(id=type_id).first()
    if goods_type:
        #查询所有上架商品
        goodslist = goods_type.goods_set.filter(goods_under=1)
    return render(request,"buyer/goods_list.html",locals())

def setOrderId(goods_id,user_id,store_id):
    timeId = time.strftime("%Y%m%d%H%M%S",time.localtime())
    return timeId+str(goods_id)+str(store_id)+str(user_id)

def place_order(request):
    if request.method == "POST":
        count = int(request.POST.get("count"))

        goods_id = request.POST.get("goods_id")

        user_id = request.COOKIES.get("user_id")

        goods = Goods.objects.get(id = goods_id)
        # store_id = goods.store_id.get(id=3).id
        store_id = goods.store_id.id
        price = goods.goods_price

        order = Order()
        order.order_id =setOrderId(str(user_id),str(goods_id),str(store_id))
        order.goods_count = count

        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = count*price
        order.save()

        order_detail = OrderDetail()
        order_detail.order_id =order
        order_detail.goods_id = goods_id
        order_detail.goods_name = goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count*goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_imag = goods.goods_image
        order.order_status = 1
        order_detail.save()

        detail = [order_detail]
        return render(request,"buyer/place_order.html",locals())
    else:
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.get(id = order_id)
            detail = order.objects_set.all()
            return render(request,"buyer/place_order.html",locals())
        else:
            return HttpResponse("非法请求")

def cart(request):
    user_id = request.COOKIES.get("user_id")
    goods_list = Cart.objects.filter(user_id=user_id)
    if request.method == "POST":
        post_data = request.POST
        cart_data = []
        for k,v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(Cart.objects.get(id=int(v)))
        goods_count = len(cart_data)
        goods_total = sum([int(i.goods_total) for i in cart_data])

        order = Order()
        order.order_id = setOrderId(user_id,goods_count,"2")

        order.goods_count = goods_count
        order.order_user = Buyer.objects.get(id=user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()

        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_imag = detail.goods_picture
            order_detail.save()
            url = "/buyer/place_order/?order_id=%s"%order.id
            return HttpResponseRedirect(url)
    return render(request,"buyer/cart.html",locals())

def add_cart(request):
    result = {"state":"error","data":""}
    if request.method == 'POST':
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        goods = Goods.objects.get(id = int(goods_id))

        user_id = request.COOKIES.get("user_id")

        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price
        cart.goods_total = goods.goods_price*count
        cart.goods_number = count
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods.id
        cart.goods_store = goods.store_id.id
        cart.user_id = user_id
        cart.save()
        result["state"] = "success"
        result["data"] = "购物车添加成功"
    else:
        result["data"] = "请求失败"
    return JsonResponse(result)


# Create your views here.
