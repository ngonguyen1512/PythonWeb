from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('forgot/', views.forgot, name='forgot'),
    path('login/', views.loginPage, name='login'),
    path('change_password/', views.change, name='change'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.register, name='register'),

    path('all/', views.all, name='all'),
    path('cart/', views.cart, name='cart'),
    path('like/', views.like, name='like'),
    path('order/', views.order, name='order'),
    path('search/', views.search, name='search'),
    path('payment/', views.payment, name='payment'),
    path('personal/', views.personal, name='personal'),
    path('updateitem/', views.updateItem, name='updateitem'),
    path('<slug:categories>/<slug:samples>/', views.rental, name='rental'),
    path('<slug:categories>/<slug:samples>/<slug:productname>/<slug:productid>/', views.detail, name='detail'),
]

# "slug" sử dụng để chỉ một chuỗi ký tự được chuẩn hóa (phiên bản rút gọn). 
# Slug được thiết kế để chỉ chứa các chữ cái, số, gạch ngang (-) hoặc gạch dưới (_), 