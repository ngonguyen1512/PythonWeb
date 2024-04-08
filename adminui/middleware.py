import datetime
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from app.models import *
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

class AddTotalRevenueToAdmin(MiddlewareMixin):
    
    def process_template_response(self, request, response):
        if request.path.startswith('/admin/'):
            done_state = State.objects.get(name='Done')
            orders = Order.objects.filter(state=done_state)  # Filter orders where state is 'Done'
            total_revenue = sum(order.total for order in orders)
            number_of_orders = orders.count()  # Đếm số lượng hóa đơn
            # Đếm số lượng nhân viên và số lượng khách hàng
            number_of_employees = User.objects.filter(is_staff=True).count()
            number_of_customers = User.objects.filter(is_staff=False).count()
            number_of_products = Product.objects.all().count()

            # Lấy danh sách sản phẩm bán chạy
            orders = OrderDetail.objects.values(
                'product_id', 'product__name', 'product__image', 'product__price'
            ).annotate(
                total_quantity=Coalesce(Sum('quantity'), 0)
            ).order_by('-total_quantity')

            product_count = int(request.GET.get('product_count', 3))  # Default to 5 products
            top_selling_products = orders[:product_count]
            
            for product in top_selling_products:
                product['imageURL'] = product['product__image']
                product['name'] = product['product__name']
                product['price'] = product['product__price']
                del product['product__image']
                del product['product__name']
                del product['product__price']
                
            # Thu thập dữ liệu doanh thu theo từng ngày trong tuần
            current_date = datetime.date.today()
            start_date = current_date - datetime.timedelta(days=current_date.weekday())
            daily_revenue = [0, 0, 0, 0, 0, 0, 0]  # 0 = Monday, 1 = Tuesday, ... , 6 = Sunday
            daily_order_count = [0, 0, 0, 0, 0, 0, 0]  # 0 = Monday, 1 = Tuesday, ... , 6 = Sunday

            start_month = current_date.replace(day=1)  # Ngày đầu tiên của tháng
            end_month = (start_month + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)  # Ngày cuối cùng của tháng
            
            monthly_orders = Order.objects.filter(date__range=[start_month, end_month], state=done_state)
            monthly_total_revenue = sum(order.total for order in monthly_orders)
            
            for i in range(7): 
                end_date = start_date + datetime.timedelta(days=1)
                daily_orders = Order.objects.filter(date__range=[start_date, end_date], state=done_state)
                daily_total_revenue = sum(order.total for order in daily_orders)
                daily_revenue[start_date.weekday()] = daily_total_revenue
                daily_order_count[start_date.weekday()] = daily_orders.count()
                start_date = end_date
                
            weekly_revenue_dates = self.get_last_seven_days()

            response.context_data['total_revenue'] = total_revenue
            response.context_data['number_of_orders'] = number_of_orders
            response.context_data['number_of_products'] = number_of_products
            response.context_data['number_of_employees'] = number_of_employees
            response.context_data['number_of_customers'] = number_of_customers
            response.context_data['top_selling_products'] = top_selling_products
            response.context_data['product_count'] = product_count
            response.context_data['daily_revenue'] = daily_revenue
            response.context_data['daily_order_count'] = daily_order_count
            response.context_data['weekly_revenue_dates'] = weekly_revenue_dates
            response.context_data['monthly_total_revenue'] = monthly_total_revenue
            
        return response
    
    def get_last_seven_days(self):
        today = datetime.date.today()
        # Find the starting date of the current week (Monday)
        start_of_week = today - datetime.timedelta(days=today.weekday())
        
        last_seven_days = [(start_of_week + datetime.timedelta(days=i)).strftime('%d/%m') for i in range(0, 7)]
        return last_seven_days

