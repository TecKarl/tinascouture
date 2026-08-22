from django import forms

from .models import Apparel, Perfume, Size


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class ProductImageUploadMixin:
    extra_images = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={"accept": "image/*"}),
        help_text="Optional: select multiple gallery images.",
    )


class ApparelCreateForm(ProductImageUploadMixin, forms.ModelForm):
    class Meta:
        model = Apparel
        fields = ("name", "description", "price", "stock", "main_image", "is_active", "sizes")
        widgets = {"sizes": forms.CheckboxSelectMultiple}

    sizes = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )


class PerfumeCreateForm(ProductImageUploadMixin, forms.ModelForm):
    class Meta:
        model = Perfume
        fields = ("name", "brand", "description", "volume_ml", "price", "stock", "main_image", "is_active")


class ApparelEditForm(ApparelCreateForm):
    main_image = forms.ImageField(required=False)


class PerfumeEditForm(PerfumeCreateForm):
    main_image = forms.ImageField(required=False)