import re

from django import forms
from django.utils import timezone

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "phone", "email", "address",
                  "delivery_date", "payment_method", "note"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Nguyễn Văn A"}),
            "phone": forms.TextInput(attrs={"placeholder": "0912345678", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "Không bắt buộc"}),
            "address": forms.TextInput(attrs={"placeholder": "Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành"}),
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
            "payment_method": forms.RadioSelect,
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "Ví dụ: ghi chữ lên bánh, giờ muốn nhận..."}),
        }

    def clean_phone(self):
        phone = re.sub(r"[\s.\-]", "", self.cleaned_data["phone"])
        if not re.fullmatch(r"(0|\+84)\d{9,10}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ (ví dụ: 0912345678).")
        return phone

    def clean_delivery_date(self):
        day = self.cleaned_data.get("delivery_date")
        if day and day < timezone.localdate():
            raise forms.ValidationError("Ngày nhận không được ở trong quá khứ.")
        return day
