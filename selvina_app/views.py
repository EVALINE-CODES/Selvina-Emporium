from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError

import json
import datetime

from .models import *
from .form import *
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.models import User


def home(request):
    url_configuration = URLConfiguration.get_solo()
    return render(request, "index.html", {"url_configuration": url_configuration})


def about(request):
    url_configuration = URLConfiguration.get_solo()
    return render(request, "about.html", {"url_configuration": url_configuration})


def contactFormView(request):
    url_configuration = URLConfiguration.get_solo()
    form = ContactForm()
    return render(
        request, "contact.html", {"form": form, "url_configuration": url_configuration}
    )


def contactView(request):
    url_configuration = URLConfiguration.get_solo()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            try:
                send_mail(subject, message, from_email, ["richey.fitt@gmail.com"])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("success")
    else:
        form = ContactForm()

    return render(
        request, "contact.html", {"form": form, "url_configuration": url_configuration}
    )


def successView(request):
    url_configuration = URLConfiguration.get_solo()
    messages = ContactMessage.objects.all()
    return render(request, "success.html", {"messages": messages})


def store(request):
    url_configuration = URLConfiguration.get_solo()
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    products = Product.objects.all()

    paginator = Paginator(products, 8)
    page = request.GET.get("page")

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    for product in products:
        product.rating_range = range(int(product.rating))

    context = {"products": products, "cartItems": cartItems}
    return render(request, "store.html", context)


def remove_from_wishlist(request, pk):
    url_configuration = URLConfiguration.get_solo()
    item = get_object_or_404(Wishlist, pk=pk)
    if request.method == "POST":
        if item.customer == request.user.customer:
            item.delete()
            return redirect("wishlist")
    return redirect("wishlist")


def product_detail(request, pk):
    url_configuration = URLConfiguration.get_solo()
    product = get_object_or_404(Product, pk=pk)

    return render(request, "product_detail.html", {"product": product})


def cart(request, pk=None):
    url_configuration = URLConfiguration.get_solo()
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    if pk is not None:
        product = get_object_or_404(Product, pk=pk)
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False
            )
            order_item, created = OrderItem.objects.get_or_create(
                order=order, product=product
            )
            order_item.quantity += 1
            order_item.save()
        else:
            return redirect("login")
        return redirect("cart")

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "cart.html", context)


def remove_from_cart(request, pk):
    url_configuration = URLConfiguration.get_solo()
    item = get_object_or_404(OrderItem, pk=pk)

    if request.method == "POST":
        item.delete()
        return redirect("cart")

    return redirect("cart")


def update_cart(request):
    url_configuration = URLConfiguration.get_solo()
    data = json.loads(request.body)
    product_id = data["productId"]
    action = data["action"]

    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(
        customer=request.user.customer, complete=False
    )
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        order_item.quantity += 1
    elif action == "remove":
        order_item.quantity -= 1

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    cart_items = order.orderitem_set.all()
    cart_total = sum(item.get_total() for item in cart_items)
    cart_items_count = sum(item.quantity for item in cart_items)

    response_data = {
        "cartTotal": cart_total,
        "cartItemsCount": cart_items_count,
    }

    return JsonResponse(response_data)


def checkout(request):
    # Retrieve order and product information
    customer = request.user.customer
    order = get_object_or_404(Order, customer=customer)
    products = order.orderitem_set.all().select_related("product")

    context = {
        "order": order,
        "products": products,
    }
    return render(request, "checkout.html", context)


def wishlist(request):
    customer = request.user.customer
    wishlist_items = Wishlist.objects.filter(customer=customer)
    context = {"wishlist_items": wishlist_items}
    return render(request, "wishlist.html", context)


def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user.is_authenticated:
        customer = request.user.customer
        Wishlist.objects.get_or_create(customer=customer, product=product)
        return redirect("wishlist")
    else:
        return redirect("login")


def remove_from_wishlist(request, pk):
    item = get_object_or_404(Wishlist, pk=pk)

    if request.method == "POST":
        item.delete()
        return redirect("wishlist")

    return redirect("wishlist")


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action:", action)
    print("Product:", productId)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        try:
            customer_id = request.session["customer_id"]
            customer = Customer.objects.get(id=customer_id)
        except KeyError:
            customer = Customer.objects.create(name="Guest")
            request.session["customer_id"] = customer.id
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Get the product based on the productId
    product = Product.objects.get(id=productId)
    # Get or create the order item associated with the order and product
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment submitted..", safe=False)
