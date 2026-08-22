from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Size(models.Model):
    """A selectable apparel size (S, M, L, XL) — managed as checkboxes."""

    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"
    XLARGE = "XL"
    SIZE_CHOICES = [
        (SMALL, "Small (S)"),
        (MEDIUM, "Medium (M)"),
        (LARGE, "Large (L)"),
        (XLARGE, "Extra Large (XL)"),
    ]

    code = models.CharField(max_length=2, choices=SIZE_CHOICES, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.get_code_display()


class BaseProduct(models.Model):
    """Shared fields for anything sold in the shop."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price in GHC",
    )
    stock = models.PositiveIntegerField(
        default=0, help_text="Number of units currently in stock"
    )
    main_image = models.ImageField(upload_to="products/")
    is_active = models.BooleanField(
        default=True, help_text="Untick to hide this product from the shop"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0


class Apparel(BaseProduct):
    """Shirts, PJs and other wearable pieces."""

    sizes = models.ManyToManyField(
        Size,
        blank=True,
        related_name="apparel_items",
        help_text="Tick every size currently available for this item",
    )

    class Meta(BaseProduct.Meta):
        verbose_name_plural = "Apparel"

    def get_absolute_url(self):
        return reverse("shop:apparel_detail", args=[self.pk])


class ApparelImage(models.Model):
    """Extra gallery photos shown on an apparel item's detail page."""

    product = models.ForeignKey(
        Apparel, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/apparel/extra/")
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Perfume(BaseProduct):
    """Fragrances and body splashes."""

    brand = models.CharField(max_length=120, blank=True)
    volume_ml = models.PositiveIntegerField(
        null=True, blank=True, help_text="Bottle size in millilitres, e.g. 250"
    )

    def get_absolute_url(self):
        return reverse("shop:perfume_detail", args=[self.pk])


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=30, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_username()


class Purchase(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="purchases")
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)
    delivery_address = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Purchase #{self.pk} - {self.customer_name}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    product_type = models.CharField(max_length=20, choices=[("apparel", "Apparel"), ("perfume", "Perfume")])
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=2, blank=True)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class PerfumeImage(models.Model):
    """Extra gallery photos shown on a perfume's detail page."""

    product = models.ForeignKey(
        Perfume, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/perfume/extra/")
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
