from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category, Product

def product_list(request):
    products = Product.objects.select_related('category').all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    categories = Category.objects.all()
    return render(request, 'inventory/product_list.html', {
        'products': products,
        'categories': categories,
    })

def product_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        low_stock_threshold = request.POST.get('low_stock_threshold', 5)
        if not all([name, category_id, price]):
            messages.error(request, 'Nombre, categoría y precio son obligatorios.')
            return render(request, 'inventory/product_form.html', {'categories': categories})
        category = get_object_or_404(Category, id=category_id)
        Product.objects.create(
            name=name, description=description, category=category,
            price=price, stock=stock, low_stock_threshold=low_stock_threshold,
        )
        messages.success(request, 'Producto creado exitosamente.')
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'categories': categories})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        category_id = request.POST.get('category')
        if category_id:
            product.category = get_object_or_404(Category, id=category_id)
        product.price = request.POST.get('price', product.price)
        product.stock = request.POST.get('stock', product.stock)
        product.low_stock_threshold = request.POST.get('low_stock_threshold', product.low_stock_threshold)
        product.save()
        messages.success(request, 'Producto actualizado exitosamente.')
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'product': product, 'categories': categories})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})