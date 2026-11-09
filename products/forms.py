from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={
                "rows": 4, "maxlength": 1000,
                "placeholder": "Chia sẻ cảm nhận của bạn về chiếc bánh này (không bắt buộc)...",
            }),
        }
