import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.utils import timezone

User = get_user_model()


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Họ và tên", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Tên đăng nhập"
        self.fields["password1"].label = "Mật khẩu"
        self.fields["password2"].label = "Nhập lại mật khẩu"
        self.fields["first_name"].widget.attrs["placeholder"] = "Nguyễn Văn A"
        self.fields["email"].widget.attrs["placeholder"] = "ban@example.com"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email


class ProfileForm(forms.Form):
    """Sửa thông tin cá nhân: họ tên + email (bảng User) và số điện thoại, địa chỉ, ngày sinh (bảng Profile)."""

    full_name = forms.CharField(label="Họ và tên", max_length=150)
    email = forms.EmailField(label="Email")
    phone = forms.CharField(label="Số điện thoại", max_length=20, required=False)
    address = forms.CharField(label="Địa chỉ giao hàng mặc định", max_length=255, required=False)
    birth_date = forms.DateField(label="Ngày sinh", required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, user, profile, **kwargs):
        self.user = user
        self.profile = profile
        if not args and "initial" not in kwargs:
            kwargs["initial"] = {
                "full_name": user.first_name,
                "email": user.email,
                "phone": profile.phone,
                "address": profile.address,
                "birth_date": profile.birth_date,
            }
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs["placeholder"] = "Nguyễn Văn A"
        self.fields["phone"].widget.attrs.update({"placeholder": "0912345678", "inputmode": "tel"})
        self.fields["address"].widget.attrs["placeholder"] = "Số nhà, đường, phường/xã, quận/huyện, tỉnh/thành"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Email này đã được tài khoản khác sử dụng.")
        return email

    def clean_phone(self):
        phone = re.sub(r"[\s.\-]", "", self.cleaned_data.get("phone", ""))
        if phone and not re.fullmatch(r"(0|\+84)\d{9,10}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ (ví dụ: 0912345678).")
        return phone

    def clean_birth_date(self):
        day = self.cleaned_data.get("birth_date")
        if day and day > timezone.localdate():
            raise forms.ValidationError("Ngày sinh không được ở tương lai.")
        return day

    def save(self):
        data = self.cleaned_data
        self.user.first_name = data["full_name"].strip()
        self.user.email = data["email"]
        self.user.save(update_fields=["first_name", "email"])
        self.profile.phone = data["phone"]
        self.profile.address = data["address"].strip()
        self.profile.birth_date = data["birth_date"]
        self.profile.save()


class VNPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Mật khẩu hiện tại"
        self.fields["new_password1"].label = "Mật khẩu mới"
        self.fields["new_password2"].label = "Nhập lại mật khẩu mới"
