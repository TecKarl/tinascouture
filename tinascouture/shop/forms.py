from django import forms
from django.contrib.auth.models import User

from .models import Apparel, CustomerProfile, Perfume, Size


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30)
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.profile = getattr(user, "profile", None)
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial.update(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=self.profile.phone if self.profile else "",
                address=self.profile.address if self.profile else "",
            )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("That email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        query = CustomerProfile.objects.filter(phone=phone)
        if self.profile:
            query = query.exclude(pk=self.profile.pk)
        if query.exists():
            raise forms.ValidationError("That phone number is already registered.")
        return phone


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