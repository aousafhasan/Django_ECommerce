from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import InterestForm, OrderForm, ForgotPasswordForm, RegisterForm
from datetime import date
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import hashlib
import random
import string
from django.contrib import messages

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Category, Product, Client, Order
from datetime import datetime

# Create your views here.


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if 'last_login' in request.session:
                    messages.success(request, 'Last login date and time: ' + str(request.session['last_login']))
                else:
                    request.session['last_login'] = str(timezone.now())
                    # print(request.session['last_login'])
                    messages.success(request, "Your last login was more than 1 hour ago")

                request.session['last_login'] = str(timezone.now())

                request.session['username'] = username
                request.session['user_first_name'] = user.first_name
                request.session['user_last_name'] = user.last_name
                request.session.set_expiry(3600)

                return HttpResponseRedirect(reverse('myapp:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('myapp:login'))

def index(request):
    cat_list = Category.objects.all().order_by('id')[:10]
    return render(request, 'myapp/index.html', {'cat_list': cat_list})
    product_list = Product.objects.all().order_by('-price')[:5]
    response = HttpResponse()
    heading1 = '<p>' + 'List of categories: ' + '</p>'
    response.write(heading1)
    for category in cat_list:
        para = '<p>'+ str(category.id) + ': ' + str(category) + '</p>'
        response.write(para)
    heading2 = '<p>' + 'List of products: ' + '</p>'
    response.write(heading2)
    for product in product_list:
        para = '<p>' + str(product.id)+':' + str(product) + '</p>'
        response.write(para)
    return response


def about(request):
    # return render(request, 'myapp/about.html')
    # return HttpResponse("This is an online store App")

    if 'about_visits' in request.COOKIES:
        count_visited = int(request.COOKIES['about_visits'])
        response = render(request, 'myapp/about.html', {'no_of_times_visited': count_visited + 1})
        response.set_cookie('about_visits', count_visited + 1, max_age=300)
    else:
        response = render(request, 'myapp/about.html', {'no_of_times_visited': 1})
        response.set_cookie('about_visits', 1)
    return response


def detail(request, cat_no):
    category = get_object_or_404(Category, pk=cat_no)
    products = Product.objects.filter(category=category)
    return render(request, 'myapp/detail.html', {'category': category, 'products': products})
    # detail_response = HttpResponse()
    # heading = '<p>' + 'Warehouse location :' + category.warehouse + '</p>'
    # heading += '<p>' + 'List of products' + '</p>'
    # detail_response.write(heading)
    #
    # for product in products:
    #     para = '<p>' + str(product.id) + ':' + str(product) + '</p>'
    #     detail_response.write(para)
    # return detail_response

def products(request):
    prodlist = Product.objects.all().order_by('id')[:10]
    return render(request, 'myapp/products.html', {'prodlist': prodlist})

def place_order(request):
    msg = ''
    prodlist = Product.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST, initial={'status_date': date.today(), 'order_status': 'Order Placed'})
        if form.is_valid():
            order = form.save(commit=False)
            if order.num_units <= order.product.stock:
                prod = Product.objects.filter(id=order.product.id).first()
                prod.stock -= order.num_units
                prod.save()
                order.save()
                msg = 'Your order has been placed successfully'
            else:
                msg = 'We do not have sufficient stock to fill your order.'
            return render(request, 'myapp/order_response.html', {'msg': msg})

    else:
        form = OrderForm()
        return render(request, 'myapp/placeorder.html', {'form': form, 'msg': msg, 'prodlist': prodlist})

def productdetail(request, prod_id):
    prod = Product.objects.get(pk=prod_id)
    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['interested'] == 'Yes':
                prod.interested = prod.interested + 1
                print(prod.id)
                prod.save()
                return redirect('/myapp/')
            else :
                return redirect('/myapp/')
    else:
        form = InterestForm()
        return render(request, 'myapp/productdetail.html', {'form': form, 'prod': prod})

@login_required
def myorders(request):
    try:
        user = request.user
        print(user)
        client = Client.objects.get(username=user.username)
        orders = Order.objects.filter(client=client)
        msg = f'Orders placed by {client} :-'
        if orders.count() == 0:
            msg = 'Client has not placed any orders'
        return render(request, 'myapp/myorders.html', {'orders': orders, 'msg': msg})
    except Client.DoesNotExist:
        msg = 'You are not a registered client'
        return render(request, 'myapp/myorders.html', {'msg': msg})

def user_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("myapp:login")
        else:
            print('form invalid')
    else:
        form = RegisterForm()
    return render(request=request, template_name="myapp/register.html", context={"register_form": form})

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            random_password = ''.join(random.choice(string.ascii_letters) for i in range(10))
            password = make_password(random_password)
            Client.objects.filter(email=form.cleaned_data['Email']).update(password=password)

            subject = 'New Password'
            message = 'Your new password is ' + random_password
            recipient = form.cleaned_data['Email']
            send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently=False)
            return HttpResponse('A password has been sent to your inbox')
        else:
            return HttpResponse('Incorrect details')
    else:
        form = ForgotPasswordForm()
        return render(request, 'myapp/forgot_password.html', {'form': form})

