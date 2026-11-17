from django import forms


class DiscountForm(forms.Form):
    direction = forms.ChoiceField(
        label="Kiểu thay đổi", initial="down", widget=forms.RadioSelect,
        choices=[("down", "Giảm giá"), ("up", "Tăng giá")],
    )
    percent = forms.IntegerField(label="Phần trăm (%)", min_value=1, max_value=90, initial=10)
    round_to = forms.ChoiceField(
        label="Làm tròn giá mới", initial="1000",
        choices=[("0", "Không làm tròn"), ("500", "Làm tròn đến 500đ"), ("1000", "Làm tròn đến 1.000đ")],
    )


class RestockForm(forms.Form):
    quantity = forms.IntegerField(label="Số lượng nhập thêm", min_value=1, max_value=100000, initial=10)
