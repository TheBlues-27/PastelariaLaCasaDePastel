import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Import csrf_exempt
from django.db import transaction
from django.shortcuts import render, redirect # Ensure redirect is imported
from django.contrib.auth import authenticate, login, logout # Import authentication functions
from django.contrib.auth.decorators import login_required # Import login_required decorator
from .models import Product, Order, OrderItem, AccompanimentItem
from django.forms.models import model_to_dict

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

@csrf_exempt # Add this decorator if you're not handling CSRF tokens in the view itself
def save_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_number = data.get('table_number')
            cart_items_data = data.get('cart_items')

            if not table_number or not cart_items_data:
                return JsonResponse({'message': 'Missing table number or cart items'}, status=400)

            total_order_price = Decimal('0.00')
            
            # Calculate total price from cart items
            for item_id, item_data in cart_items_data.items():
                product_price = Decimal(str(item_data['price']))
                quantity = item_data['quantity']
                total_order_price += product_price * quantity

                if 'accompaniments' in item_data:
                    for acc_id, acc_data in item_data['accompaniments'].items():
                        acc_price = Decimal(str(acc_data['price']))
                        acc_quantity = acc_data['quantity']
                        total_order_price += acc_price * acc_quantity

            # Create the Order instance
            order = Order.objects.create(
                table_number=table_number,
                total_price=total_order_price # <--- CHANGE 'total' to 'total_price' here
            )

            # Save OrderItems and AccompanimentItems
            for item_id, item_data in cart_items_data.items():
                try:
                    product = Product.objects.get(id=item_id)
                except Product.DoesNotExist:
                    # Handle case where product might have been deleted
                    product = None 

                order_item = OrderItem.objects.create(
                    order=order,
                    product=product, # Can be None if product was deleted
                    name=item_data['name'],
                    price=Decimal(str(item_data['price'])),
                    quantity=item_data['quantity']
                )

                if 'accompaniments' in item_data:
                    for acc_id, acc_data in item_data['accompaniments'].items():
                        try:
                            acc_product = Product.objects.get(id=acc_id)
                        except Product.DoesNotExist:
                            acc_product = None

                        AccompanimentItem.objects.create(
                            order_item=order_item,
                            product=acc_product, # Can be None if product was deleted
                            name=acc_data['name'],
                            price=Decimal(str(acc_data['price'])),
                            quantity=acc_data['quantity']
                        )

            return JsonResponse({'message': 'Order saved successfully', 'order_id': order.id})

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            print(f"Error saving order: {e}") # Log the actual error for debugging
            return JsonResponse({'message': f'Erro ao salvar o pedido: {str(e)}'}, status=500)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


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

def get_order_history(request, table_number):
    if request.method == 'GET':
        try:
            orders = Order.objects.filter(table_number=table_number).order_by('-timestamp')
            
            orders_data = []
            for order in orders:
                order_items = OrderItem.objects.filter(order=order)
                items_data = []
                for item in order_items:
                    item_dict = model_to_dict(item, fields=['name', 'price', 'quantity'])
                    
                    accompaniment_items = AccompanimentItem.objects.filter(order_item=item)
                    accompaniments_data = []
                    for acc_item in accompaniment_items:
                        accompaniments_data.append(model_to_dict(acc_item, fields=['name', 'price', 'quantity']))
                    item_dict['accompaniments'] = accompaniments_data
                    items_data.append(item_dict)
                
                orders_data.append({
                    'id': order.id,
                    'timestamp': order.timestamp.isoformat(),
                    'table_number': order.table_number,
                    'total_price': order.total_price,
                    'items': items_data
                })
            
            return JsonResponse({'orders': orders_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)