from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='pos-index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('save_order/', views.save_order, name='save_order'),
    path('login/', views.user_login, name='login'), # New login URL
    path('logout/', views.user_logout, name='logout'), # New logout URL
    path('get_order_history/<int:table_number>/', views.get_order_history, name='get_order_history'),
]