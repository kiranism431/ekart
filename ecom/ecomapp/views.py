from django.shortcuts import render, HttpResponse, redirect
from ecomapp import urls
from ecomapp import models
from ecomapp.models import Product, Cart, Order, MyOrder
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail
from django.shortcuts import redirect

# Create your views here.
def register(request):
    if request.method == 'GET':
        return render(request, "Register.html")
    else:
        nm = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['ucpass']
        # print(nm)
        # print(p)
        # print(cp)
        context = {}
        if p != cp:
            context['errormsg'] = "Password do not match"
            return render(request,"Register.html",context)

        elif len(p) > 5:
            context['errormsg'] = " password length 5 is mandatory"
            return render(request,"Register.html",context)
        
        else:
            try:
                u = User.objects.create(username = nm)
                u.set_password(p)
                u.save()
                context['success'] = "Successfully Registered!!!"
                return render(request,"Register.html",context)
            except:
                context['errormsg'] = 'User already exists!!'
                return render(request, "Register.html", context)
        # return HttpResponse("Successfully Registered!!")

def user_login(request):
    if request.method == 'GET':
        return render(request, "login.html")
    else:
        nm = request.POST['uname']
        p = request.POST['upass']
        u = authenticate(username = nm, password = p)
        # print(u)
        if u is not None:
            login(request, u)
            return redirect ("/home")
        else:
            context = {}
            context['errormsg'] = 'Username and Password is incorrect'
        return render(request, "login.html", context)
        # return HttpResponse("Sussessfully Loggedin!!")

def user_logout(request):
    logout(request)
    return render(request, "login.html")

def search(request):
    context = {}
    query = request.POST['query']
    print(query)
    pname = Product.objects.filter(name__icontains = query)    #alternative for like operator command in sql
    pdetails = Product.objects.filter(pdetails__icontains = query)
    pcat = Product.objects.filter(cat__icontains = query)
    allproducts = pname.union(pdetails, pcat)
    if len(allproducts) == 0:
        context['errmsg'] = "Product Not Found"
    context['data'] = allproducts
    return render(request, "index.html", context)
    return HttpResponse("query fetched !!")

def home(request):
    m = Product.objects.filter(is_active = True)
    # print(m)
    context = {}
    context['data'] = m

    return render(request, "index.html", context)   

def product_details(request, prod_id):
    p = Product.objects.filter(id = prod_id)
    context = {}
    context ['data'] = p

    return render(request, 'product details.html', context)

def cart(request, prod_id):
    if request.user.is_authenticated:
        u = User.objects.filter(id = request.user.id)
        # print(u[0])
        p = Product.objects.filter(id = prod_id)

        q1 = Q(user_id = u[0])
        q2 = Q(pid = p[0])
        c = Cart.objects.filter(q1 & q2)
        n = len(c)
        context = {}
        context['data'] = p
        if n==1:
            context['errormsg'] = "Product already exist in cart!!"
            return render(request, "product details.html", context)
        else:
            c = Cart.objects.create(user_id = u[0], pid = p[0])
            c.save()
            context['errormsg1'] = "Product successfully added to the cart !!"
            return render(request, "product details.html", context)

    else:
        return redirect("/login")

        return HttpResponse("User fetched")

def updateqty(request,x,cid):
    c = Cart.objects.filter(id = cid)
    q = c[0].qty
    if x == '1':
        q = q+1
    elif q>1:
        q = q-1
    c.update(qty = q)
    return redirect("/viewcart")

def viewcart(request):
    c = Cart.objects.filter(user_id = request.user.id)
    # print(c)
    # print(c[0])
    # print(c[0].user_id.is_staff)
    # print(c[0].pid.details)
    tot = 0
    for x in c:
        tot = tot + x.pid.price * x.qty
    context = {}
    context['data'] = c
    context['totamt'] = tot
    context['n']= len(c)
    return render(request, "cart.html", context)

def remove(request, cid):
    c = Cart.objects.filter(id =cid)
    c.delete()
    context={}
    context['data'] =c
    return redirect("/viewcart")

def remove_order(request, oid):
    print(oid)
    c = Cart.objects.filter(id =oid)
    c.delete()
    context={}
    context['data'] = oid
    return redirect("/fetchorder")

def placeorder(request):
    c = Cart.objects.filter(user_id = request.user.id)
    o_id = random.randrange(1000, 9999)
    for x in c :
        amount = x.pid.price * x.qty
        o = Order.objects.create(order_id =o_id, user_id = x.user_id, 
                                 amt = amount, qty = x.qty, pid = x.pid)
        o.save()
        x.delete()
    return redirect ("/fetchorder")

def fetchorder(request):
    orders = Order.objects.filter(user_id = request.user.id)
    tot = 0
    for x in orders:
        tot = tot + x.amt

    context  = {}
    context ['orders'] = orders
    context ['tamt'] = tot
    context ['n'] = len(orders)
    return render(request, "placeorder.html", context)

def paymentsuccess(request):
    sub = "Ekart-order status"
    msg = "thanks for shopping ,  shopmore !!"
    frm = "kiranpahadi431@gmail.com"
    u = User.objects.filter(id = request.user.id)
    to = "vrushali@itvedant.com"
    send_mail(
        sub,
        msg,
        frm,
        [to],
        fail_silently=False
    )    
    ord = Order.objects.filter(id = request.user.id)
    for x in ord:
        mo = MyOrder.objects.create(order_id = x.order_id,
                                    user_id = x.user_id,
                                    pid = x.pid,
                                    amt = x.amt)
        mo.save()
        x.delete()
    return HttpResponse("payment successfull !")


def makepayment(request):
    client = razorpay.Client(auth=("rzp_test_R7kWkFU6ZllnWF", "W0gE85soRmV6WanAQr1nW69n"))
    ord = Order.objects.filter(user_id = request.user.id)
    tot = 0
    for x in ord:
        tot = tot + x.amt
        oid = x.order_id
        
    data = {"amount":tot*100, "currency": "INR", "receipt": "oid"}
    payment = client.order.create(data = data)
    print (payment)
    context ={}
    context['payment']= payment
    return render(request, "pay.html", context)

def catfilter(request, cv):
    print(cv)
    if cv == 1:
        q1 = Q(cat = 'Mobile')
    elif cv == 2:
        q1 = Q(cat = 'Shoes')
    else:
        q1 = Q(cat = 'Clothes')

    q2 = Q(is_active = True)

    p = Product.objects.filter(q1 & q2)
    print(p)
    context = {}
    context['data'] = p
    return render(request, "index.html", context)

def sort(request, sv):
    if sv == '1':
        p = Product.objects.order_by('-price').filter(is_active = True)
    else:
        p = Product.objects.order_by('price').filter(is_active = True)
    context = {}
    context['data'] = p   
    return render(request, "index.html", context)

def filterbyprice(request):
    min = request.POST['min']
    max = request.POST['max']

    q1 = Q(price__gte = min)
    q2 = Q(price__lte = max)

    p = Product.objects.filter(q1 & q2)
    context = {}
    context['data'] = p
    return render(request, "index.html", context)