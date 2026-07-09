from django import forms
from .models import Product, Category, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock', 'low_stock_threshold']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].required = False
        self.fields['low_stock_threshold'].required = False

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('El precio debe ser mayor a cero.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            stock = 0
        if stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['quantity', 'movement_type', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 2}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
