import time
import hashlib

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.core.paginator import Paginator

from Store.models import *
from Buyer.models import *

#登陆验证
def loginvaild(fun):
    """
    登陆验证
    没有登陆，进入主页会跳转登录页
    """
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username") #获取cookie值
        s_user = request.session.get("username") #获取session值
        if c_user and s_user and c_user ==s_user: #如果cookie和session值存在且相等
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/store/login/')
    return inner#1 返回inner函数

#密码加密
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

#注册用户
def register(request):
    """
    register注册
    返回注册页面
    进行注册数据保存
    """
    if request.method == "POST":#判断前端页面提交form方式
        username = request.POST.get("username")#从前端获取数据
        password = request.POST.get("password")

        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = setPassword(password)#加密
            seller.nickname = username#昵称
            seller.save()#保存
            return HttpResponseRedirect('/store/login/')#跳到登陆页
    return render(request,'store/register.html',locals())#前端渲染

def login(request):
    """
    登录页
    进行cookies和sessions验证
    """
    response = render(request, "store/login.html")  # 1 前端渲染
    response.set_cookie("login_form","login_page")#设置登陆时用的cookies
    if request.method == "POST": #3判断请求方式是否为post
        username = request.POST.get("username")#4 获取前端用户名
        password = request.POST.get("password")#5 获取前端密码
        if username and password: #6 判断用户名和密码是否为空
            user = Seller.objects.filter(username=username).first()#7 获取数据库此用户对象
            if user:#8 判断此用户是否存在
                web_password = setPassword(password)#9 将前端密码加密
                cookies = request.COOKIES.get("login_form")#10 获取cookies的key的值
                if user.password == web_password and cookies == "login_page":#11 判断密码和cookie值是否相等
                    response = HttpResponseRedirect("/store/index/")#12 相等转到首页

                    response.set_cookie("username",username)#13 设置新的cookie值
                    response.set_cookie("user_id",user.id)
                    request.session['username'] = username#14 设置session值
                    store = Store.objects.filter(user_id = user.id).first()#验证店铺是否存在
                    if store:
                        response.set_cookie("has_store",store.id)
                    else:
                        response.set_cookie("has_store","")
                    return response# 15 返回首页
    return response #16 前面的不成立返回登录页


#主页
@loginvaild
def index(request):
    """
    当直接进入index时会调用loginvalid登陆验证
    添加检查账号是否有店铺的逻辑
    """
    return render(request,"store/index.html")

#


#模板页没用以后删除测试用途
def base(request):
    return render(request,"store/base.html")

#注册店铺
@loginvaild
def register_store(request):
    type_list = StoreType.objects.all()#获取店铺类型
    if request.method == "POST":
        post_data = request.POST#得到前端form数据

        store_name = post_data.get("store_name")
        store_description = post_data.get("store_description")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        store_address = post_data.get("store_address")

        user_id = int(request.COOKIES.get("user_id"))#显示登陆用户

        type_list = post_data.get("type")#store与store_type多对多

        store_logo = request.FILES.get("store_logo")#文件格式

        store = Store()#数据写入

        store.store_name = store_name
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo

        store.save()
        #多对多 字段
        for i in type_list:#一条一条写入type
            store_type = StoreType.objects.get(id = i)
            store.type.add(store_type)
        store.save()
        response = HttpResponseRedirect("/store/index/")
        response.set_cookie("has_store",store.id)#设置cookies用来显示当前用户是否有店铺
        return response
    return render(request,'store/register_store.html',locals())

#添加商品
@loginvaild
def add_goods(request):
    """
    添加商品
    :param request:
    :return:
    """
    goods_style_list = GoodsType.objects.all()#
    if request.method =="POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_data = request.POST.get("goods_data")
        goods_safeData = request.POST.get("goods_safeData")
        goods_store = request.COOKIES.get("has_store")
        goods_image= request.FILES.get("goods_image")
        goods_type = request.POST.get("goods_type")

        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_data = goods_data
        goods.goods_safeData = goods_safeData
        goods.goods_store = goods_store
        goods.goods_image = goods_image
        goods.goods_type = GoodsType.objects.get(id=int(goods_type))
        goods_store_id = Store.objects.get(id = int(goods_store))
        goods.save()
        #多对多数据
        # goods.store_id.add(
        #     Store.objects.get(id=int(goods_store))
        # )
        goods.save()
        return HttpResponseRedirect("/store/gl/up/")
    return render(request,"store/add_goods.html",locals())

#商品列表
@loginvaild
def goods_list(request,state):
    if state =="up":#url参数up为上架商品
        state_num = 1
    else:
        state_num = 0

    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)#获取页面的参数page_num
    store_id = request.COOKIES.get("has_store")#获取当前当铺的id
    store = Store.objects.get(id=int(store_id))#从数据中查到当前店铺的数据
    if keywords:#搜索框的关键字
        goods_list = store.goods_set.filter(goods_name__contains=keywords,goods_under=state_num)#从数据库中模糊查询

    else:
        goods_list = store.goods_set.filter(goods_under=state_num)#查询所有
    paginator = Paginator(goods_list,6)#分页将goods_list每页显示几条数据
    page = paginator.page(int(page_num))#获取当前页的数据
    page_range = paginator.page_range#返回页码列表

    return render(request,"store/goods_list.html",locals())

@loginvaild
def goods(request,goods_id):
    #从goods_list.html链接的地址栏参数的id

    goods_data = Goods.objects.filter(id=goods_id).first()#

    return render(request,"store/goods.html",locals())

#修改商品
@loginvaild
def update_goods(request,goods_id):
    #goods_id 路由匹配 goods.html 当前商品id
    goods_data = Goods.objects.filter(id=goods_id).first()#

    if request.method =="POST":#form请求
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_data = request.POST.get("goods_data")
        goods_safeData = request.POST.get("goods_safeData")
        goods_store = request.POST.get("goods_store")
        goods_image= request.FILES.get("goods_image")


        goods = Goods.objects.get(id=int(goods_id))
        #查询当前商品id的数据修改
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_data = goods_data
        goods.goods_safeData = goods_safeData
        goods.goods_store = goods_store
        if goods_image:
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect('/store/goods/%s/'%goods_id)
        #多对多数据
    return render(request, "store/update_goods.html", locals())

#修改商品上架，下架，销毁
@loginvaild
def set_goods(request,state):
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get("id")#当前这一商品列表页的商品id id为地址栏数据 goods_list.html
    referer = request.META.get("HTTP_REFERER")#HTTP请求的Header信息 HTTP_REFERER，进站前链接网页
    if id:
        goods = Goods.objects.filter(id=id).first()#从goods查询出此id的数据
        if state == "delete":
            goods.delete()#删除
        else:
            goods.goods_under = state_num#修改商品状态
            goods.save()
    return HttpResponseRedirect(referer)#返回上个页面

#登出
@loginvaild
def logout(request):
    response = HttpResponseRedirect("/store/login/")
    for key in request.COOKIES:
        response.delete_cookie(key)#删除cookies
    return response

#添加商品类型
@loginvaild
def add_goods_style(request):
    if request.method =="POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        picture = request.FILES.get("picture")

        goods = GoodsType()

        goods.name = name
        goods.description = description
        goods.picture = picture
        goods.save()
        return HttpResponseRedirect("/store/gsl/")
    return render(request,"store/add_goods_style.html",locals())

#商品类型列表
@loginvaild
def goods_style_list(request):

    page_num = request.GET.get("page_num", 1)  # 获取页面的参数page_num

    goods_style = GoodsType.objects.all()  # 从数据中查到当前店铺的数据

    paginator = Paginator(goods_style, 6)  # 分页将goods_list每页显示几条数据
    page = paginator.page(int(page_num))  # 获取当前页的数据
    page_range = paginator.page_range  # 返回页码列表

    return render(request, "store/goods_style_list.html", locals())

#订单列表
def order_list(request):
    store_id = request.COOKIES.get("has_store")
    order_list = OrderDetail.objects.filter(order_id__order_status=2,goods_store=store_id)
    return render(request,"store/order_list.html",locals())

# Create your views here.
