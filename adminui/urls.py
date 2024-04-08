from django.urls import path
from .views import custom_admin_index

urlpatterns = [
    path('', custom_admin_index, name='dashboard'),  # Đặt tên cho đường dẫn của custom_admin_index là 'dashboard'
]
