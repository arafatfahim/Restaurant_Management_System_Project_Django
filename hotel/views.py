from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from reportlab.pdfgen import canvas
from .models import Customer, Comment, Order, Food, Data, Cart, OrderContent, Staff, DeliveryBoy, UserOrder
from .forms import SignUpForm
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['firstname']
            user.last_name = form.cleaned_data['lastname']
            user.email = form.cleaned_data['email']
            user.username = user.email.split('@')[0]
            user.set_password(form.cleaned_data['password'])
            user.save()
            address = form.cleaned_data['address']
            contact = form.cleaned_data['contact']
            customer = Customer.objects.create(customer=user, address=address, contact=contact)
            customer.save()
            return redirect('http://localhost:8000/accounts/login/')

    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
@staff_member_required
def dashboard_admin(request):
    comments = Comment.objects.count()
    orders = Order.objects.count()
    customers = Customer.objects.count()
    completed_orders = Order.objects.filter(payment_status="Completed")
    top_customers = Customer.objects.filter().order_by('-total_sale')
    latest_orders = Order.objects.filter().order_by('-order_timestamp')
    datas = Data.objects.filter().order_by('date')
    sales = 0
    for order in completed_orders:
        sales += order.total_amount

    context = {
        'comments': comments,
        'orders': orders,
        'customers': customers,
        'sales': sales,
        'top_customers': top_customers,
        'latest_orders': latest_orders,
        'datas': datas,
    }
    return render(request, 'admin_temp/index.html', context)


@login_required
@staff_member_required
def users_admin(request):
    customers = Customer.objects.filter()
    # print(customers)
    return render(request, 'admin_temp/users.html', {'users': customers})


@login_required
@staff_member_required
def orders_admin(request):
    orders = Order.objects.filter().order_by('-id')
    dBoys = Staff.objects.filter(role='Delivery Boy')
    # print(dBoys)
    # print(orders)
    return render(request, 'admin_temp/orders.html', {'orders': orders, 'dBoys': dBoys})


@login_required
@staff_member_required
def foods_admin(request):
    foods = Food.objects.filter()
    return render(request, 'admin_temp/foods.html', {'foods': foods})


@login_required
@staff_member_required
def sales_admin(request):
    sales = Data.objects.filter()
    return render(request, 'admin_temp/sales.html', {'sales': sales})


def menu(request):
    cuisine = request.GET.get('cuisine')
    # print(cuisine)
    if cuisine is not None:
        if (cuisine == "Gujarati") or (cuisine == "Punjabi"):
            foods = Food.objects.filter(status="Enabled", course=cuisine)
        elif cuisine == "south":
            foods = Food.objects.filter(status="Enabled", course="South Indian")
        elif cuisine == "fast":
            foods = Food.objects.filter(course="Fast")
    else:
        foods = Food.objects.filter()
    return render(request, 'menu.html', {'foods': foods, 'cuisine': cuisine})


def index(request):
    food = Food.objects.filter().order_by('-num_order')
    return render(request, 'index.html', {'food': food})


@login_required
@staff_member_required
def confirm_order(request, orderID):
    order = Order.objects.get(id=orderID)
    order.confirmOrder()
    order.save()
    customerID = order.customer.id
    customer = Customer.objects.get(id=customerID)
    customer.total_sale += order.total_amount
    customer.orders += 1
    customer.save()
    return redirect('hotel:orders_admin')


@login_required
@staff_member_required
def confirm_delivery(request, orderID):
    to_email = []
    order = Order.objects.get(id=orderID)
    order.confirmDelivery()
    order.save()
    # mail_subject = 'Order Delivered successfully'
    # to = str(order.customer.customer.email)
    # to_email.append(to)
    # from_email = ''
    # message = "Hi "+order.customer.customer.first_name+" Your order was delivered successfully. Please go to your dashboard to see your order history. <br> Your order id is "+orderID+". Share ypour feedback woth us."
    # send_mail(
    #     mail_subject,
    #     message,
    #     from_email,
    #     to_email,
    # )
    return redirect('hotel:orders_admin')


# @staff_member_required
class StaffAdmin(LoginRequiredMixin, TemplateView):
    model = Staff
    template_name = 'admin_temp/staff.html'

    def get_context_data(self, **kwargs):
        context = super(StaffAdmin, self).get_context_data(**kwargs)
        context['staffs'] = Staff.objects.all()  # .order_by('id')[:5]
        return context


# @staff_member_required
class AddStaffView(LoginRequiredMixin, CreateView):
    model = Staff
    fields = ['staff_name', 'address', 'contact', 'salary', 'role']
    template_name = 'admin_temp/add_staff.html'
    success_url = reverse_lazy('hotel:staff_admin')


# @staff_member_required
class FoodUpdateView(LoginRequiredMixin, UpdateView):
    model = Food
    fields = ['name', 'course', 'content_description', 'ingradients',
              'base_price', 'sale_price', 'discount', 'image'
              ]
    template_name = 'admin_temp/update_food.html'
    success_url = reverse_lazy('hotel:foods_admin')


# @staff_member_required
class FoodDeleteView(LoginRequiredMixin, DeleteView):
    model = Food
    template_name = 'admin_temp/food_del.html'
    success_url = reverse_lazy('hotel:foods_admin')


class StaffDeleteView(LoginRequiredMixin, DeleteView):
    model = Staff
    template_name = 'admin_temp/staff_del.html'
    success_url = reverse_lazy('hotel:staff_admin')


# @login_required
# @staff_member_required
# def edit_food(request, foodID):
#     food = Food.objects.filter(id=foodID)[0]
#     if request.method == "POST":
#         if request.POST['base_price'] != "":
#             food.base_price = request.POST['base_price']
#
#         if request.POST['discount'] != "":
#             food.discount = request.POST['discount']
#
#         food.sale_price = (100 - float(food.discount))*float(food.base_price)/100
#
#         status = request.POST.get('disabled')
#         print(status)
#         if status == 'on':
#             food.status = "Disabled"
#         else:
#             food.status = "Enabled"
#
#         food.save()
#     return redirect('hotel:foods_admin')


@login_required
@staff_member_required
def add_user(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        contact = request.POST['contact']
        email = request.POST['email']
        password = request.POST['password']
        confirm_pass = request.POST['confirm_password']
        username = email.split('@')[0]

        if (first_name == "") or (last_name == "") or (address == "") or (contact == "") or (email == "") or (
                password == "") or (confirm_pass == ""):
            customers = Customer.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/users.html', {'users': customers, 'error_msg': error_msg})

        if password == confirm_pass:
            user = User.objects.create(username=username, email=email, password=password, first_name=first_name,
                                       last_name=last_name)
            user.save()
            cust = Customer.objects.create(customer=user, address=address, contact=contact)
            cust.save()
            success_msg = "New user successfully created"
            customers = Customer.objects.filter()
            return render(request, 'admin_temp/users.html', {'users': customers, 'success_msg': success_msg})

    return redirect('hotel:users_admin')


@login_required
@staff_member_required
def add_food(request):
    if request.method == "POST":
        name = request.POST['name']
        course = request.POST['course']
        ingradients = request.POST['ingradients']
        content = request.POST['content']
        base_price = request.POST['base_price']
        discount = request.POST['discount']
        sale_price = (100 - float(discount)) * float(base_price) / 100
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)

        if (name == "") or (course is None) or (content == "") or (ingradients == "") or (base_price == "") or (
                discount == ""):
            foods = Food.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/foods.html', {'foods': foods, 'error_msg': error_msg})

        food = Food.objects.create(name=name, course=course, content_description=content, ingradients=ingradients,
                                   base_price=base_price, discount=discount, sale_price=sale_price, image=filename)
        food.save()
        foods = Food.objects.filter()
        success_msg = "Please enter valid details"
        return render(request, 'admin_temp/foods.html', {'foods': foods, 'success_msg': success_msg})
    return redirect('hotel:foods_admin')


class Add_DeliveryBoy(LoginRequiredMixin, TemplateView):
    model = Order, Staff
    fields = ['order.id', 'staff_id']
    template_name = 'admin_temp/assign_db.html'
    success_url = reverse_lazy('hotel:staff_admin')


class Thanks(LoginRequiredMixin, TemplateView):
    template_name = 'thankyou.html'


@login_required
@staff_member_required
def add_deliveryBoy(request, orderID):
    order = Order.objects.get(id=orderID)
    dName = request.POST['deliveryBoy']
    # print(dName)
    # user = User.objects.get(first_name=dName)
    deliveryBoy = Staff.objects.get(staff_name=dName)
    order.delivery_boy = deliveryBoy
    order.save()
    return redirect('hotel:orders_admin')


@login_required
@staff_member_required
def add_sales(request):
    if request.method == "POST":
        date = request.POST['date']
        sales = request.POST['sales']
        expenses = request.POST['expenses']

        if (date is None) or (sales == "") or (expenses == ""):
            sales = Data.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/sales.html', {'sales': sales, 'error_msg': error_msg})

        data = Data.objects.create(date=date, sales=sales, expenses=expenses)
        data.save()
        datas = Data.objects.filter()
        success_msg = "Sales data added successfully!"
        return render(request, 'admin_temp/sales.html', {'sales': datas, 'success_msg': success_msg})

    return redirect('hotel:foods_admin')


@login_required
@staff_member_required
def edit_sales(request, saleID):
    data = Data.objects.filter(id=saleID)[0]
    if request.method == "POST":
        if request.POST['sales'] != "":
            data.sales = request.POST['sales']

        if request.POST['expenses'] != "":
            data.expenses = request.POST['expenses']

        data.save()
    return redirect('hotel:sales_admin')


@login_required
def food_details(request, foodID):
    food = Food.objects.get(id=foodID)
    return render(request, 'user/single2.html', {'food': food})


@login_required
def addTocart(request, foodID, userID):
    food = Food.objects.get(id=foodID)
    user = User.objects.get(id=userID)
    cart = Cart.objects.create(food=food, user=user)
    cart.save()
    return redirect('hotel:cart')


@login_required
def delete_item(request, ID):
    item = Cart.objects.get(id=ID)
    item.delete()
    return redirect('hotel:cart')


@login_required
def cart(request):
    user = User.objects.get(id=request.user.id)
    items = Cart.objects.filter(user=user)
    product = request.POST.get('product')
    remove = request.POST.get('remove')
    cart = request.session.get('cart')
    total = 0
    for item in items:
        total += item.food.sale_price
    return render(request, 'cart.html', {'items': items, 'total': total})


@login_required
def placeOrder(request):
    to_email = []
    customer = Customer.objects.get(customer=request.user)
    # print(customer.address)
    items = Cart.objects.filter(user=request.user)
    # food = items.food
    # print(items)
    total = 0
    store_all = []
    price_all = []
    for item in items:
        food = item.food
        price = item.food.sale_price
        total += item.food.sale_price
        store_all.append(food)
        data = ", \n".join(map(str, store_all))
        price_all.append(price)
        price_data = " \n".join(map(str, price_all))

    print(price_data)
    # print(total)
    # print(data)
    # i = 0
    # price = []
    # for i in items:
    #     food = item.food.sale_price
    #     # f = item.food.sale_price
    #     price.append(food)
    #     f = " \n".join(map(str, price))
    # print(f)

    order = Order.objects.create(customer=customer, order_timestamp=timezone.now(), payment_status="Pending",
                                 delivery_status="Pending", food_items=data, food_price=price_data,  total_amount=total,
                                 payment_method="Cash On Delivery", location=customer.address)
    order.save()
    # orderContent = OrderContent(food=items.food, order=order)
    # orderContent.save()
    # user_order = UserOrder(customer=customer, food_items=str(items), total_price=items.sale_price)
    items.delete()
    # mail_subject = 'Order Placed successfully'
    # to = str(customer.customer.email)
    # to_email.append(to)
    # from_email = ''
    # message = "Hi "+customer.customer.first_name+" Your order was placed successfully. Please go to your dashboard to see your order history. <br> Your order id is "+order.id+""
    # send_mail(
    #     mail_subject,
    #     message,
    #     from_email,
    #     to_email,
    # )
    return redirect('hotel:thanks')


@login_required
def latest_order(request):
    user = User.objects.get(id=request.user.id)
    customer = Customer.objects.get(customer=user)
    order = Order.objects.filter(customer=customer).order_by('-id')


@login_required
def my_orders(request):
    user = User.objects.get(id=request.user.id)
    customer = Customer.objects.get(customer=user)
    orders = Order.objects.filter(customer=customer).order_by('-id')
    # print(orders)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def delivery_boy(request):
    user = User.objects.get(id=request.user.id)
    try:
        customer = Customer.objects.get(customer=user)
    except Customer.DoesNotExist:
        staff = Staff.objects.get(staff_name=user)
        if staff is None or staff.role != 'Delivery Boy':
            redirect('hotel:index')
        else:
            orders = DeliveryBoy.objects.filter(delivery_boy=staff)
            return render(request, 'delivery_boy.html', {'orders': orders})

    return redirect('hotel:index')


class OrderListView(ListView):
    model = Order
    template_name = 'orders.html'


def customer_render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    order = get_object_or_404(Order, pk=pk)
    template_path = 'pdf1.html'
    context = {'order': order}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, )
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def render_pdf_view(request):
    pass

    # template_path = 'pdf1.html'
    # context = {'myvar': 'this is your template context'}
    # # Create a Django response object, and specify content_type as pdf
    # response = HttpResponse(content_type='application/pdf')
    #
    # # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # response['Content-Disposition'] = 'filename="report.pdf"'
    # # find the template and render it.
    # template = get_template(template_path)
    # html = template.render(context)
    #
    # # create a pdf
    # pisa_status = pisa.CreatePDF(
    #     html, dest=response, )
    # # if error then show some funny view
    # if pisa_status.err:
    #     return HttpResponse('We had some errors <pre>' + html + '</pre>')
    # return response
