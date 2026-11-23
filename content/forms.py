import re

from django import forms

from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    # Ô ẩn để chặn bot: người thật không thấy nên sẽ để trống.
    website = forms.CharField(required=False, label="", widget=forms.TextInput(attrs={
        "tabindex": "-1", "autocomplete": "off", "aria-hidden": "true",
    }))

    class Meta:
        model = JobApplication
        fields = ["full_name", "phone", "email", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Nguyễn Văn A"}),
            "phone": forms.TextInput(attrs={"placeholder": "0912345678", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "ban@email.com"}),
            "message": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Vài dòng giới thiệu kinh nghiệm, hoặc dán link CV (Google Drive, LinkedIn...)",
            }),
        }

    def clean_phone(self):
        phone = re.sub(r"[\s.\-]", "", self.cleaned_data["phone"])
        if not re.fullmatch(r"(0|\+84)\d{9,10}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ (ví dụ: 0912345678).")
        return phone

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Không thể gửi biểu mẫu.")
        return ""
