from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Apparel, ApparelImage, CustomerProfile, Perfume, PerfumeImage, Purchase, PurchaseItem, Size


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("code",)


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    fields = ("product_type", "product_id", "product_name", "quantity", "unit_price", "line_total", "size")
    readonly_fields = fields

    @admin.display(description="Line total")
    def line_total(self, obj):
        return obj.line_total

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("__str__", "customer_name", "customer_email", "customer_phone", "total", "created_at")
    list_filter = ("created_at",)
    search_fields = ("customer_name", "customer_email", "customer_phone")
    readonly_fields = (
        "user", "customer_name", "customer_email", "customer_phone",
        "delivery_address", "total", "status", "created_at",
    )
    inlines = [PurchaseItemInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address")


class ApparelImageInline(admin.TabularInline):
    model = ApparelImage
    extra = 1


class ApparelAdminForm(forms.ModelForm):
    class Meta:
        model = Apparel
        fields = "__all__"
        widgets = {
            # Renders the available sizes as a bunch of selectable checkboxes
            # (S / M / L / XL) instead of a multi-select dropdown.
            "sizes": forms.CheckboxSelectMultiple,
        }


@admin.register(Apparel)
class ApparelAdmin(admin.ModelAdmin):
    form = ApparelAdminForm
    list_display = ("thumb", "name", "price", "stock", "size_list", "is_active")
    list_editable = ("price", "stock", "is_active")
    list_filter = ("is_active", "sizes")
    search_fields = ("name", "description")
    inlines = [ApparelImageInline]
    fieldsets = (
        (None, {"fields": ("name", "description", "is_active")}),
        ("Pricing & Inventory", {"fields": ("price", "stock")}),
        ("Available sizes", {"fields": ("sizes",)}),
        ("Main Image", {"fields": ("main_image",)}),
    )

    @admin.display(description="Image")
    def thumb(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="height:45px;width:45px;object-fit:cover;'
                'border-radius:6px;" />',
                obj.main_image.url,
            )
        return "—"

    @admin.display(description="Sizes")
    def size_list(self, obj):
        return ", ".join(s.code for s in obj.sizes.all()) or "—"


class PerfumeImageInline(admin.TabularInline):
    model = PerfumeImage
    extra = 1


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "brand", "volume_ml", "price", "stock", "is_active")
    list_editable = ("price", "stock", "is_active")
    list_filter = ("is_active", "brand")
    search_fields = ("name", "brand", "description")
    inlines = [PerfumeImageInline]
    fieldsets = (
        (None, {"fields": ("name", "brand", "description", "is_active")}),
        ("Pricing & Inventory", {"fields": ("price", "stock", "volume_ml")}),
        ("Main Image", {"fields": ("main_image",)}),
    )

    @admin.display(description="Image")
    def thumb(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="height:45px;width:45px;object-fit:cover;'
                'border-radius:6px;" />',
                obj.main_image.url,
            )
        return "—"


admin.site.site_header = "Tina's Couture Admin"
admin.site.site_title = "Tina's Couture Admin"
admin.site.index_title = "Manage apparel, perfumes, images and stock"
