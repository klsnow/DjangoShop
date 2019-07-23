import time
import hashlib

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.core.paginator import Paginator

from Store.models import *

#登陆验证
def loginvaild(fun):
    """
    登陆验证
    没有登陆，进入主页会跳转登录页

    """
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")#获取cookie值
        s_user = request.session.get("username")#获取session值
        if c_user and s_user and c_user ==s_user:#如果cookie和session值存在且相等
            user = Seller.objects.filter(username = c_user).first()#当直接访问主页时判断刚才登陆时的cookies值是否与username相等
            if user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/store/login')
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
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username,password)
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = setPassword(password)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect('/store/login/')
    return render(request,'store/register.html',locals())

#登陆
def login(request):
    """
    登录页
    进行cookies和sessions验证
    """
    response = render(request,"store/login.html")#1 设置返回页面
    response.set_cookie("login_form","login_page")#2 设置cookies值
    if request.method == "POST": #3判断请求方式是否为post
        username = request.POST.get("username")#4 获取前端用户名
        password = request.POST.get("password")#5 获取前端密码
        if username and password:#6 判断用户名和密码是否为空
            user = Seller.objects.filter(username=username).first()#7 获取数据库此用户对象
            if user:#8 判断此用户是否存在
                web_password = setPassword(password)#9 将前端密码加密
                cookies = request.COOKIES.get("login_form")#10 获取cookies的key的值
                if user.password ==web_password and cookies == "login_page":#11 判断密码和cookie值是否相等
                    response = HttpResponseRedirect("/store/index/")#12 相等转到首页
                    response.set_cookie("username",username)#13 设置新的cookie值
                    response.set_cookie("user_id",user.id)
                    request.session['username'] = username#14 设置session值
                    return response# 15 返回首页
    return response #16 前面的不成立返回登录页

#主页
@loginvaild
def index(request):
    """
    当直接进入index时会调用loginvalid登陆验证
    添加检查账号是否有店铺的逻辑
    """
    #查询当前用户id
    user_id = request.COOKIES.get("user_id")
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    #通过用户查询店铺是否存在，店和用户通过user_id进行关联
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0

    return render(request,"store/index.html",{"is_store":is_store})

#
def button(request):
    return render(request,"store/button.html")

#模板页没用以后删除测试用途
def base(request):
    return render(request,"store/base.html")

#注册店铺
def register_store(request):
    type_list = StoreType.objects.all()#获取店铺类型
    if request.method == "POST":
        post_data = request.POST#得到前端数据

        store_name = post_data.get("store_name")
        store_description = post_data.get("store_description")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        store_address = post_data.get("store_address")

        user_id = int(request.COOKIES.get("user_id"))#显示登陆用户

        type_list = post_data.get("type")#store与store_type多对多
        store_logo = request.FILES.get("store_logo")

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
    return render(request,'store/register_store.html',locals())

#添加商品
def add_goods(request):
    """
    添加商品
    :param request:
    :return:
    """
    if request.method =="POST":
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_data = request.POST.get("goods_data")
        goods_safeData = request.POST.get("goods_safeData")
        goods_store = request.POST.get("goods_store")
        goods_image= request.FILES.get("goods_image")


        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_data = goods_data
        goods.goods_safeData = goods_safeData
        goods.goods_store = goods_store
        goods.goods_image = goods_image
        goods.save()
        #多对多数据
        goods.store_id.add(
            Store.objects.get(id=int(goods_store))
        )
        goods.save()
        return HttpResponseRedirect("/store/gl/")
    return render(request,"store/add_goods.html")

#商品列表
def goods_list(request):
    keywords = request.GET.get("keywords","")
    page_num = request.GET.get("page_num",1)#获取页面的参数page_num
    if keywords:#搜索框的关键字
        goods_list = Goods.objects.filter(goods_name__contains=keywords)#从数据库中模糊查询
    else:
        goods_list = Goods.objects.all()#查询所有
    paginator = Paginator(goods_list,6)#分页将goods_list每页显示几条数据
    page = paginator.page(int(page_num))#获取当前页的数据
    page_range = paginator.page_range#返回页码列表
    #{"page":page,"page_range":page_range,"keywords":keywords}
    return render(request,"store/goods_list.html",locals())




# Create your views here.
