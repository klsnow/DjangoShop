import time
import hashlib

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import HttpResponseRedirect

from Store.models import *


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

def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


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
                    request.session['username'] = username#14 设置session值
                    return response# 15 返回首页
    return response #16 前面的不成立返回登录页

@loginvaild
def index(request):
    """
    当直接进入index时会调用loginvalid登陆验证

    """
    return render(request,"store/index.html",locals())



# Create your views here.
