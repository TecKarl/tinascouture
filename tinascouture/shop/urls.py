from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.product_list, name="product_list"),
    path("apparel/<int:pk>/", views.apparel_detail, name="apparel_detail"),
    path("perfumes/<int:pk>/", views.perfume_detail, name="perfume_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<str:product_type>/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<str:product_type>/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/checkout/", views.cart_checkout, name="cart_checkout"),
    path("orders/", views.customer_orders, name="customer_orders"),
    path("orders/<int:pk>/cancel/", views.customer_cancel_order, name="customer_cancel_order"),
    path("manage/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/orders/", views.admin_orders, name="admin_orders"),
    path("manage/orders/<int:pk>/status/", views.admin_update_order_status, name="admin_update_order_status"),
    path("manage/products/add/<str:product_type>/", views.admin_product_add, name="admin_product_add"),
    path("manage/products/<str:product_type>/<int:pk>/edit/", views.admin_product_edit, name="admin_product_edit"),
]
