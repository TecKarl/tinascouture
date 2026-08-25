from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from functools import wraps

from .cart import Cart, get_product_model
from .forms import ApparelCreateForm, ApparelEditForm, PerfumeCreateForm, PerfumeEditForm
from .models import Apparel, ApparelImage, CustomerProfile, Perfume, PerfumeImage, Purchase, PurchaseItem



def health_check(request):
    return JsonResponse({"status": "ok"})

def customer_only(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("shop:admin_dashboard")
        return view(request, *args, **kwargs)

    return wrapped


def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:admin_dashboard" if request.user.is_staff else "shop:product_list")
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        user = User.objects.filter(email__iexact=identifier).first()
        if user is None:
            profile = CustomerProfile.objects.filter(phone=identifier).select_related("user").first()
            user = profile.user if profile else None
        user = authenticate(
            request,
            username=user.get_username() if user else identifier,
            password=request.POST.get("password"),
        )
        if user is not None:
            login(request, user)
            destination = "shop:admin_dashboard" if user.is_staff else (request.POST.get("next") or "shop:product_list")
            return redirect(destination)
        messages.error(request, "Invalid username or password.")
    return render(request, "shop/login.html", {"next": request.GET.get("next", "")})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("shop:admin_dashboard" if request.user.is_staff else "shop:product_list")
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        if not first_name or not last_name or not email or not phone or not password:
            messages.error(request, "Please complete every field.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "That email is already registered.")
        elif CustomerProfile.objects.filter(phone=phone).exists():
            messages.error(request, "That phone number is already registered.")
        else:
            username = email
            try:
                validate_password(password)
            except Exception as error:
                messages.error(request, " ".join(error.messages))
                return render(request, "shop/signup.html")
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            CustomerProfile.objects.create(user=user, phone=phone)
            login(request, user)
            return redirect("shop:product_list")
    return render(request, "shop/signup.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("shop:login")


@customer_only
@login_required
def product_list(request):
    """The gallery / homepage — apparel and perfumes, shown separately."""
    apparel = Apparel.objects.filter(is_active=True).prefetch_related("sizes")
    perfumes = Perfume.objects.filter(is_active=True)
    return render(
        request, "shop/index.html", {"apparel": apparel, "perfumes": perfumes}
    )


@customer_only
@login_required
def apparel_detail(request, pk):
    product = get_object_or_404(Apparel, pk=pk, is_active=True)
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "product_type": "apparel"},
    )


@customer_only
@login_required
def perfume_detail(request, pk):
    product = get_object_or_404(Perfume, pk=pk, is_active=True)
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "product_type": "perfume"},
    )


@require_POST
@customer_only
@login_required
def cart_add(request, product_type, product_id):
    """Add a product to the cart, or bump/decrease its quantity.

    POST params:
      quantity          -- integer amount (default 1)
      override_quantity -- "True" to set the quantity exactly, otherwise it's
                            added to whatever is already in the cart.
      next               -- optional URL to redirect back to.
    """
    cart = Cart(request)
    model = get_product_model(product_type)
    product = get_object_or_404(model, id=product_id)
    size = request.POST.get("size", "").strip().upper()
    if product_type == "apparel" and not product.sizes.filter(code=size).exists():
        messages.error(request, "Please select an available size.")
        return redirect(product.get_absolute_url())

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    override_quantity = request.POST.get("override_quantity") == "True"
    cart.add(
        product=product,
        product_type=product_type,
        quantity=quantity,
        override_quantity=override_quantity,
        size=size,
    )

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("shop:cart_detail")


@require_POST
@customer_only
@login_required
def cart_remove(request, product_type, product_id):
    cart = Cart(request)
    model = get_product_model(product_type)
    product = get_object_or_404(model, id=product_id)
    cart.remove(product, product_type, request.POST.get("size", ""))
    return redirect("shop:cart_detail")


@customer_only
@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, "shop/cart.html", {"cart": cart})


@require_POST
@transaction.atomic
@customer_only
@login_required
def cart_checkout(request):
    """Finalise the order: reduce stock for everything in the cart."""
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    unavailable = []
    for item in cart:
        model = get_product_model(item["product_type"])
        product = model.objects.select_for_update().get(pk=item["product"].pk)
        if product.stock < item["quantity"]:
            unavailable.append(product.name)

    if unavailable:
        messages.error(
            request,
            "Sorry, stock changed for: " + ", ".join(unavailable) +
            ". Please review your cart.",
        )
        return redirect("shop:cart_detail")

    order_items = list(cart)
    profile = getattr(request.user, "profile", None)
    purchase = Purchase.objects.create(
        user=request.user,
        customer_name=request.user.get_full_name() or request.user.get_username(),
        customer_email=request.user.email,
        customer_phone=profile.phone if profile else "",
        delivery_address=profile.address if profile else "",
        total=cart.get_total_price(),
    )
    for item in order_items:
        model = get_product_model(item["product_type"])
        product = model.objects.select_for_update().get(pk=item["product"].pk)
        product.stock -= item["quantity"]
        product.save()
        PurchaseItem.objects.create(
            purchase=purchase,
            product_type=item["product_type"],
            product_id=product.pk,
            product_name=product.name,
            unit_price=item["price"],
            quantity=item["quantity"],
            size=item["size"],
        )

    total = cart.get_total_price()
    cart.clear()

    return render(
        request,
        "shop/checkout_success.html",
        {"order_items": order_items, "total": total, "purchase": purchase},
    )


@customer_only
@login_required
def customer_orders(request):
    purchases = request.user.purchases.prefetch_related("items").all()
    return render(request, "shop/orders.html", {"purchases": purchases})


@require_POST
@customer_only
@login_required
def customer_cancel_order(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, user=request.user)
    if purchase.status in {"pending", "confirmed"}:
        purchase.status = "cancelled"
        purchase.save(update_fields=["status"])
        messages.success(request, f"Order #{purchase.pk} was cancelled.")
    elif purchase.status == "cancelled":
        messages.info(request, f"Order #{purchase.pk} is already cancelled.")
    else:
        messages.error(request, "Completed orders can no longer be cancelled.")
    return redirect("shop:customer_orders")


def is_staff(user):
    return user.is_active and user.is_staff


@user_passes_test(is_staff, login_url="shop:login")
def admin_dashboard(request):
    purchases = Purchase.objects.select_related("user")[:10]
    return render(request, "shop/admin_dashboard.html", {
        "purchases": purchases,
        "apparel": Apparel.objects.all(),
        "perfumes": Perfume.objects.all(),
        "apparel_count": Apparel.objects.count(),
        "perfume_count": Perfume.objects.count(),
    })


@user_passes_test(is_staff, login_url="shop:login")
@transaction.atomic
def admin_product_add(request, product_type):
    form_class = ApparelCreateForm if product_type == "apparel" else PerfumeCreateForm if product_type == "perfume" else None
    if form_class is None:
        from django.http import Http404
        raise Http404

    form = form_class(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        image_model = ApparelImage if product_type == "apparel" else PerfumeImage
        for image in request.FILES.getlist("extra_images"):
            image_model.objects.create(product=product, image=image)
        messages.success(request, f"{product.name} was added to the shop.")
        return redirect("shop:admin_dashboard")
    return render(request, "shop/admin_product_form.html", {
        "form": form,
        "product_type": product_type,
        "product": None,
        "title": "Add apparel" if product_type == "apparel" else "Add perfume",
    })


@user_passes_test(is_staff, login_url="shop:login")
@transaction.atomic
def admin_product_edit(request, product_type, pk):
    if product_type == "apparel":
        model, form_class, image_model = Apparel, ApparelEditForm, ApparelImage
    elif product_type == "perfume":
        model, form_class, image_model = Perfume, PerfumeEditForm, PerfumeImage
    else:
        from django.http import Http404
        raise Http404

    product = get_object_or_404(model, pk=pk)
    form = form_class(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        for image in request.FILES.getlist("extra_images"):
            image_model.objects.create(product=product, image=image)
        messages.success(request, f"{product.name} was updated.")
        return redirect("shop:admin_dashboard")
    return render(request, "shop/admin_product_form.html", {
        "form": form,
        "product_type": product_type,
        "title": f"Edit {product.name}",
    })


@user_passes_test(is_staff, login_url="shop:login")
def admin_orders(request):
    purchases = Purchase.objects.prefetch_related("items").select_related("user")
    return render(request, "shop/admin_orders.html", {"purchases": purchases})


@require_POST
@user_passes_test(is_staff, login_url="shop:login")
def admin_update_order_status(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    status = request.POST.get("status")
    allowed_statuses = {"pending", "confirmed", "completed"}
    if status not in allowed_statuses:
        messages.error(request, "That order status cannot be assigned by an admin.")
    else:
        purchase.status = status
        purchase.save(update_fields=["status"])
        messages.success(request, f"Order #{purchase.pk} is now {purchase.get_status_display().lower()}.")
    return redirect("shop:admin_orders")
