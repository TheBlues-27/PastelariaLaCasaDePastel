import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render, redirect # Ensure redirect is imported
from django.contrib.auth import authenticate, login, logout # Import authentication functions
from django.contrib.auth.decorators import login_required # Import login_required decorator
from .models import Product, Order, OrderItem

@login_required # Protect the POS page
def index(request):
    categories = [
        ('tradicional', 'Sabores Tradicionais'),
        ('acompanhamento', 'Acompanhamentos'),
        ('especial', 'Sabores Especiais'),
        ('doce', 'Sabores Doces'),
        ('bebida', 'Bebidas'),
    ]
    products_by_category = {
        key: Product.objects.filter(category=key)
        for key, _ in categories
    }
    return render(request, 'pos/index.html', {
        'products_by_category': products_by_category,
        'categories': categories,
    })

@login_required # Protect the dashboard page
def dashboard(request):
    orders = Order.objects.order_by('-created_at')
    total_sales = sum(order.total for order in orders)
    total_orders = orders.count()
    return render(request, 'pos/dashboard.html', {
        'orders': orders,
        'total_sales': total_sales,
        'total_orders': total_orders,
    })

@csrf_exempt # For simplicity during development. In production, use csrf_token in frontend.
def save_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_number = data.get('table_number')
            cart_data = data.get('cart_items')

            if table_number is None or not cart_data:
                return JsonResponse({'status': 'error', 'message': 'Dados do pedido incompletos.'}, status=400)

            total_order_price = 0
            order_items_to_create = []

            with transaction.atomic():
                for product_id_str, item_data in cart_data.items():
                    product_id = int(product_id_str)
                    try:
                        product = Product.objects.get(id=product_id)
                    except Product.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': f'Produto com ID {product_id} não encontrado.'}, status=404)

                    item_total = product.price * item_data['quantity']
                    total_order_price += item_total
                    order_items_to_create.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'price': product.price
                    })

                    if 'accompaniments' in item_data and item_data['accompaniments']:
                        for acc_id_str, acc_data in item_data['accompaniments'].items():
                            acc_id = int(acc_id_str)
                            try:
                                acc_product = Product.objects.get(id=acc_id)
                            except Product.DoesNotExist:
                                return JsonResponse({'status': 'error', 'message': f'Acompanhamento com ID {acc_id} não encontrado.'}, status=404)
                            
                            acc_item_total = acc_product.price * acc_data['quantity']
                            total_order_price += acc_item_total
                            order_items_to_create.append({
                                'product': acc_product,
                                'quantity': acc_data['quantity'],
                                'price': acc_product.price
                            })

                order = Order.objects.create(
                    table_number=table_number,
                    total=total_order_price
                )

                for item_data in order_items_to_create:
                    OrderItem.objects.create(order=order, **item_data)

            return JsonResponse({'status': 'success', 'order_id': order.id, 'total': order.total})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Requisição inválida (JSON malformado).'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('pos-index') # Redirect to the POS page
        else:
            return render(request, 'pos/login.html', {'error': 'Nome de usuário ou senha inválidos.'})
    return render(request, 'pos/login.html')

def user_logout(request):
    logout(request)
    return redirect('login') # Redirect to login page after logout