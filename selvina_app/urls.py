# from django.conf import settings
# from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/submit/", views.contactView, name="contact_submit"),
    path("contact/", views.contactView, name="contact"),
    path("success/", views.successView, name="success"),
    path("store/", views.store, name="store"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart", views.cart, name="cart"),
    path("add_to_cart/<int:pk>/", views.cart, name="add_to_cart"),
    path("remove_from_cart/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("update_cart/", views.update_cart, name="update_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add_to_wishlist/<int:pk>/", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "remove_from_wishlist/<int:pk>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path(
        "remove_from_wishlist/<int:pk>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
]
