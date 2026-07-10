import csv
from functools import wraps
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Sum, F, Count, Q
from django.utils import timezone
from .models import Category, Product, StockMovement, CompanySettings
from .forms import ProductForm, CategoryForm, StockMovementForm


def require_permission(perm):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f'/login/?next={request.path}')
            if not request.user.has_perm(perm):
                messages.error(request, 'No tienes permiso para realizar esta acción.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


@login_required
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


@login_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

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
        'query': query,
    })


@require_permission('inventory.add_product')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})


@require_permission('inventory.change_product')
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {'form': form, 'product': product})


@require_permission('inventory.delete_product')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('product_list')
    return render(request, 'inventory/product_confirm.html', {'product': product})


@login_required
def category_list(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories})


@require_permission('inventory.add_category')
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form})


@require_permission('inventory.change_category')
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {'form': form, 'category': category})


@require_permission('inventory.delete_category')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
        return redirect('category_list')
    return render(request, 'inventory/category_confirm.html', {'category': category})


@login_required
def movement_list(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    movements = product.movements.all()
    return render(request, 'inventory/movement_list.html', {
        'product': product,
        'movements': movements,
    })


@require_permission('inventory.add_stockmovement')
def movement_create(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.product = product
            if movement.movement_type == 'exit':
                movement.quantity = min(movement.quantity, product.stock)
            movement.save()
            delta = movement.quantity if movement.movement_type == 'entry' else -movement.quantity
            Product.objects.filter(pk=product.pk).update(stock=F('stock') + delta)
            product.refresh_from_db()
            messages.success(request, 'Movimiento registrado exitosamente.')
            return redirect('movement_list', product_pk=product.pk)
    else:
        form = StockMovementForm()
    return render(request, 'inventory/movement_form.html', {
        'form': form,
        'product': product,
    })


@login_required
def product_export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response['Content-Disposition'] = f'attachment; filename="productos_{timestamp}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Descripción', 'Categoría', 'Precio', 'Stock', 'Umbral de stock bajo'])
    products = Product.objects.select_related('category').all()
    for p in products:
        writer.writerow([
            p.name,
            p.description,
            p.category.name if p.category else '',
            str(p.price),
            p.stock,
            p.low_stock_threshold,
        ])
    return response


@user_passes_test(lambda u: u.is_superuser)
def settings_update(request):
    settings = CompanySettings.load()
    if request.method == 'POST':
        settings.company_name = request.POST.get('company_name', 'Mi Empresa')
        settings.currency_symbol = request.POST.get('currency_symbol', '$')
        if 'logo' in request.FILES:
            settings.logo = request.FILES['logo']
        settings.save()
        messages.success(request, 'Configuración actualizada exitosamente.')
        return redirect('settings_update')
    return render(request, 'inventory/company_settings_form.html', {
        'settings': settings,
    })
