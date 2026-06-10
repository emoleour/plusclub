from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import Product
from .forms import ProductForm

def is_admin(user):
    return user.role in ['admin', 'superadmin']

#Представления для админов
@login_required
@user_passes_test(is_admin)
def admin_product_list(request):
    products = Product.objects.all()
    return render(request, 'products/admin_product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def admin_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар создан')
            return redirect('admin_product_list')
    else:
        form = ProductForm()
    return render(request, 'products/admin_product_form.html', {'form': form, 'action': 'create'})

@login_required
@user_passes_test(is_admin)
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар обновлен.')
            return redirect('admin_product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/admin_product_form.html', {'form': form, 'action': 'update', 'product': product})

@login_required
@user_passes_test(is_admin)
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар удален.')
        return redirect('admin_product_list')
    return render(request, 'products/admin_product_confirm_delete.html', {'product': product})


def product_catalog(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    return render(request, 'products/catalog.html', {'products': products})




# Create your views here.
