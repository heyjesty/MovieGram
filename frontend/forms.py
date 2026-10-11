from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from frontend.models import Order


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class CheckoutForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        validators=[RegexValidator(r"^\+?[0-9 \-]{7,20}$", "Enter a valid phone number.")],
    )

    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "address"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}
