from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F
from .models import Category, Product


def dashboard(request):
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=F('low_stock_threshold')).count()
    total_categories = Category.objects.count()
    total_value = Product.objects.aggregate(
        total=Sum(F('price') * F('stock'))
    )['total'] or 0
    latest_products = Product.objects.select_related('category').order_by('-created_at')[:5]
    low_stock_list = Product.objects.filter(stock__lte=F('low_stock_threshold')).order_by('stock')[:5]

    return render(request, 'inventory/dashboard.html', {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_categories': total_categories,
        'total_value': total_value,
        'latest_products': latest_products,
        'low_stock_list': low_stock_list,
    })


def product_list(request):
    products = Product.objects.select_related('category').all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')

    valid_sorts = ['name', 'price', 'stock']
    if sort in valid_sorts:
        order = f'-{sort}' if direction == 'desc' else sort
        products = products.order_by(order)

    base_params = request.GET.copy()
    base_params.pop('page', None)
    base_encoded = base_params.urlencode()

    sort_links = {}
    for field in valid_sorts:
        if sort == field:
            new_dir = 'desc' if direction == 'asc' else 'asc'
        else:
            new_dir = 'asc'
        params = base_params.copy()
        params['sort'] = field
        params['dir'] = new_dir
        sort_links[field] = params.urlencode()

    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'current_sort': sort,
        'current_dir': direction,
        'sort_links': sort_links,
        'base_encoded': base_encoded,
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
    return render(request, 'inventory/product_confirm.html', {'product': product})
