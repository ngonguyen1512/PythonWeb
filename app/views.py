import re
import ssl
import json
import random
import string
import smtplib
import pandas as pd
from .models import *
from itertools import chain
from django.contrib import messages
from django.http import JsonResponse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.paginator import Paginator, EmptyPage
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth import authenticate, login, logout
from sklearn.feature_extraction.text import TfidfVectorizer
from django.shortcuts import render, get_object_or_404, redirect
ssl._create_default_https_context = ssl._create_unverified_context
from django.db.models import Sum, Case, Value, When, Q, Value, Count, When, IntegerField

# * _active_samples là biến toàn cục để lưu trữ kết quả của hàm get_active_samples()
_active_samples = None 
DONE_STATE = State.objects.get(name='Done')
ACTIVE_STATE = State.objects.get(name='Active')
NO_ACTIVE_STATE = State.objects.get(name='No active')

# * Các hàm tái sử dụng
def get_active_samples():
    global _active_samples
    if _active_samples is None:
        _active_samples = Sample.objects.filter(state=ACTIVE_STATE)
    return _active_samples

def toggle_like_status(customer, product_id):
    like_exists = Like.objects.filter(customer=customer, product_id=product_id).exists()
    if like_exists:
        Like.objects.filter(customer=customer, product_id=product_id).delete()
    else:
        Like.objects.create(customer=customer, product_id=product_id)

def generate_random_password():
    return ''.join(random.choices(string.digits, k=8))

def calculate_discounted_price(product):
    return product.price * (100 - product.discount) / 100

def get_cart_items(customer):
    if customer:
        cart, created = Cart.objects.get_or_create(customer=customer)
        items = CartDetail.objects.filter(cart=cart)
        # Phương thức aggregate() cho phép thực hiện các phép toán tổng hợp trên các trường của QuerySet.
        total_items = items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return cart, items, total_items
    else:
        return None, [], 0

def send_email(receiver_email, subject, body):
    gmail_user = 'ngonguyenkey1512@gmail.com'
    gmail_password = 'xepj ygap zlfg potx'

    message = MIMEMultipart()
    message['From'] = gmail_user
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, receiver_email, message.as_string())
        server.close()
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')

def send_email_forgot(receiver_email, username, password):
    subject = 'Password Reset'
    body = f"""
        <html>
            <body>
                <p>Dear {username},</p>
                <p>Your new password is: {password}</p>
                <p>Yours</p>
                <p>PythonWeb</p>
            </body>
        </html>
    """
    send_email(receiver_email, subject, body)

def send_email_order(receiver_email, username, orders, order_items):
    subject = 'Order Information'
    # Tạo nội dung HTML cho email
    html_content = f"""
    <html>
        <body>
            <p>Dear {username},</p>
        """
    for order in orders:
        html_content += f"""
            <p>Please find below the details of your order: {order.date}</p>
        """
        html_content += f"""
            <table class="table" style="width: 100%; overflow: auto;">
                <thead>
                    <tr>
                        <th scope="col" style="text-align: center;width: 23%">Product</th>
                        <th scope="col" style="text-align: center;width: 8%">Color</th>
                        <th scope="col" style="text-align: center;width: 8%">Size</th>
                        <th scope="col" style="text-align: center;width: 10%">Quantity</th>
                        <th scope="col" style="text-align: center;width: 15%">Price</th>
                        <th scope="col" style="text-align: center;width: 10%">Discount</th>
                        <th scope="col" style="text-align: center;width: 15%">Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
    for order_item in order_items:
            html_content += f"""
                    <tr>
                        <th>{order_item.product}</th>
                        <td style="text-align: center;">{order_item.color.name}</td>
                        <td style="text-align: center;">{order_item.size}</td>
                        <td style="text-align: center;">{order_item.quantity}</td>
                        <td style="text-align: center;">{order_item.price}</td>
                        <td style="text-align: center;">{order_item.discount}</td>
                        <td style="text-align: center;">{order_item.amount}</td>
                    </tr>
            """
    for order in orders:
            html_content += f"""
                    <tr>
                        <th colspan="6">TOTAL</th>
                        <th>{order.total}đ</th>
                    </tr>
            """
    html_content += """
                </tbody>
            </table>
            <p>Thank you for your order!</p>
            <p>Yours</p>
            <p>PythonWeb</p>
        </body>
    </html>
    """
    send_email(receiver_email, subject, html_content)

# * ALL PAGES
def logoutPage(request):
    logout(request)
    return redirect('home')

def register(request):
    total_items = 0
    if request.method == 'POST':
        username = request.POST.get('username')
        lastname = request.POST.get('lastname')
        firstname = request.POST.get('firstname')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        errors = []
        if not (username and lastname and firstname and email and password1 and password2):
            errors.append('Please fill in all fields.')
        if not email.endswith('@gmail.com'):
            errors.append('Please provide a valid Gmail address.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists!')
        if password1 != password2:
            errors.append('Confirm password incorrect!')
        if not re.search(r'\d', password1) or not re.search(r'[a-z]', password1) or not re.search(r'[A-Z]', password1) or len(password1) < 8:
            errors.append('Password must be at least 8 characters long and contain at least one digit, one lowercase letter, and one uppercase letter.')
        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password1, last_name=lastname, first_name=firstname)
            user.save()
            messages.success(request, 'Register successful!')
            return redirect('login')
        else:
            for error in errors:
                messages.error(request, error)
    context = {'samples': _active_samples, 'total_items': total_items}
    return render(request, 'app/register.html', context)

def loginPage(request):
    total_items = 0
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, 'Please fill in all fields.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin:index')
                else:
                    return redirect('home')
            else: 
                try:
                    user = User.objects.get(username=username)
                    messages.error(request, 'Password is incorrect.')
                except User.DoesNotExist:
                    messages.error(request, 'Username is not correct or does not exist.')
    context = {'samples': _active_samples, 'total_items': total_items, 'messages': messages.get_messages(request)}
    return render(request, 'app/login.html', context)

def change(request):
    customer = request.user 
    if not customer.is_authenticated: return redirect('home') 
    cart, items, total_items = get_cart_items(customer)
    if request.method == 'POST':
        password1, password2, password3 = request.POST.get('password1'), request.POST.get('password2'), request.POST.get('password3')
        errors = []
        if not customer.check_password(password1):
            errors.append('Old password is incorrect.')
        if password2 != password3:
            errors.append('New passwords do not match.')
        if not re.search(r'\d', password2) or not re.search(r'[a-z]', password2) or not re.search(r'[A-Z]', password2) or len(password2) < 8:
            errors.append('New password must contain at least 8 characters, including at least one digit, one lowercase letter, and one uppercase letter.')
        if not errors:
            customer.set_password(password2)
            customer.save()
            logout(request)
            return redirect('login')
        for error in errors:
            messages.error(request, error)
    context = {'samples': _active_samples, 'total_items': total_items, 'messages': messages.get_messages(request)}
    return render(request, 'app/client/change.html', context)

def forgot(request):
    total_items = 0
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        user = User.objects.filter(username=username, email=email).first()
        if user is not None:
            new_password = generate_random_password()
            send_email_forgot(email, username, new_password)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Sent email successful!')
            return redirect('login')
        else: 
            try:
                user = User.objects.get(username=username)
                messages.error(request, 'Email is incorrect.')
            except User.DoesNotExist:
                messages.error(request, 'Your account does not exist.')    
    context={'samples': _active_samples, 'total_items': total_items, 'messages': messages.get_messages(request)}
    return render(request, 'app/forgot.html', context)

def search(request):
    customer = request.user
    searched = ""
    products = None
    if request.method == "POST":
        searched = request.POST.get("searched", "")
        products = Product.objects.filter(name__contains=searched)
        productsid = request.POST.get('productsid')
        if customer.is_authenticated and productsid:
            toggle_like_status(customer, productsid)
    if products is not None:
        for product in products:
            product.discounted_price = calculate_discounted_price(product)
            product.is_liked = Like.objects.filter(customer=customer, product=product).exists() if customer.is_authenticated else False
    cart, items, total_items = get_cart_items(customer) if customer.is_authenticated else None, [], 0
    context = {'samples': _active_samples, "searched": searched, 'products': products, 'total_items': total_items}
    return render(request, 'app/client/search.html', context)

def personal(request):
    customer = request.user
    if not customer.is_authenticated: return redirect('home')
    cart, items, total_items = get_cart_items(customer)
    if request.method == 'POST': 
        username = request.POST.get('username')
        lastname = request.POST.get('lastname')
        firstname = request.POST.get('firstname')
        email = request.POST.get('email')
        if not (username and lastname and firstname and email):
            messages.error(request, 'Please fill in all fields.')
        elif User.objects.filter(username=username).exclude(id=customer.id).exists():
            messages.error(request, 'Username already exists, please choose another username.')
        else:
            customer.username = username
            customer.last_name = lastname
            customer.first_name = firstname
            customer.email = email
            customer.save()
            messages.success(request, 'Update information successful!')
            return redirect('personal')
    context = {'samples': _active_samples, 'total_items': total_items, 'messages': messages.get_messages(request)}
    return render(request, 'app/personal.html', context)

def order(request):
    customer = request.user
    if not customer.is_authenticated: return redirect('home')
    cart, items, total_items = get_cart_items(customer)
    orders = Order.objects.filter(customer=customer).order_by('-id') 
    order_items = OrderDetail.objects.all()
    paginator = Paginator(orders, 4)  
    page_number = request.GET.get('page', 1)
    orders = paginator.get_page(page_number)
    page_range = orders.paginator.page_range
    context = {'samples': _active_samples, 'total_items': total_items, 'order_items': order_items, 'orders': orders, 'page_range': page_range}
    return render(request, 'app/client/order.html', context)

def like(request):
    products = []
    customer = request.user
    if not customer.is_authenticated: return redirect('home')
    cart, items, total_items = get_cart_items(customer)
    liked_products = Like.objects.filter(customer=customer).values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=liked_products)
    paginator = Paginator(products, 4)  
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)
    page_range = products.paginator.page_range

    for product in products:
        product.discounted_price = calculate_discounted_price(product)
        product.is_liked = Like.objects.filter(customer=customer, product=product).exists()
    if request.method == 'POST': 
        productsid = request.POST.get('productsid')
        toggle_like_status(customer, productsid)
        return redirect(request.path)
    context = {'products': products, 'samples': _active_samples, 'total_items': total_items, 'page_range': page_range}
    return render(request, 'app/client/like.html', context)

def predict_ratings(user_id, user_product_matrix, similarity_df, k=3):
    #Lấy ra hàng của ma trận tương đồng (similarity_df) tương ứng với user_id đã cho. 
    user_similarities = similarity_df.loc[user_id]
    #ấy ra tất cả các ratings mà người dùng đã cung cấp cho các sản phẩm, được biểu diễn trong ma trận người dùng-sản phẩm (user_product_matrix).
    user_ratings = user_product_matrix.loc[user_id]
    #Xác định những sản phẩm mà người dùng chưa từng đánh giá
    unrated_items = user_ratings[user_ratings == 0].index  # Giả sử rating 0 là chưa rate
    predictions = {}
    for item in unrated_items:
        #Trích xuất ra tất cả các ratings cho sản phẩm đang được xem xét (item) từ ma trận người dùng-sản phẩm. 
        rated_by_others = user_product_matrix[item].dropna()
        #Series chứa độ tương đồng của người dùng hiện tại với tất cả người dùng khác.
        similarities = user_similarities.loc[rated_by_others.index]
        #Từ Series độ tương đồng, phương thức nlargest(k) chọn ra k giá trị cao nhất. k là số người dùng tỉnh lệ tương đồng cao nhất
        top_similar_users = similarities.nlargest(k)
        print(top_similar_users)
        #Tính tổng của tích giữa rating của các người dùng tương tự (cho sản phẩm đang xét) và độ tương đồng của họ với người dùng hiện tại.
        numerator = sum(user_product_matrix.loc[user][item] * similarity for user, similarity in top_similar_users.items())
        # Tính tổng trị tuyệt đối của độ tương đồng, dùng để chuẩn hóa tử số.
        denominator = sum(abs(similarity) for similarity in top_similar_users)
        # Nếu không có người dùng nào tương tự (hoặc độ tương đồng bằng 0), rating dự đoán sẽ được đặt là 0 để tránh lỗi chia cho 0.
        predicted_rating = numerator / denominator if denominator != 0 else 0
        #Rating dự đoán cho sản phẩm được lưu trữ trong dictionary predictions, với khóa là ID sản phẩm (item) và giá trị là rating dự đoán.
        predictions[item] = predicted_rating
    return predictions

def home(request):
    categories = Category.objects.all()
    samples_all = get_active_samples()
    
    # * Get 8 best-seller products 
    best_seller = OrderDetail.objects.values('product').annotate(total_quantity_sold=Sum('quantity')).order_by('-total_quantity_sold')[:8]
    best_seller_product_ids = [item['product'] for item in best_seller]
    sellers = Product.objects.filter(id__in=best_seller_product_ids)
    
    # * Get all promotional products
    promotions = Product.objects.filter((Q(state=ACTIVE_STATE)) & (Q(discount__gt=0)))
    all_products = Product.objects.filter(state=ACTIVE_STATE).order_by('-id')
    
    paginator = Paginator(all_products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    customer = request.user if request.user.is_authenticated else ''
    cart, items, total_items = get_cart_items(customer)
    
    # Calculate similar products based on liked products
    # # cf
    similar_products = ''
    if  customer:
        #  Truy vấn dữ liệu mua hàng và like
        customer = request.user if request.user.is_authenticated else ''
        order_details = OrderDetail.objects.all()
        likes = Like.objects.all()
        # Tạo danh sách cho orders
        order_data = [
            {'user_id': detail.order.customer.id, 'product_id': detail.product.id, 'score': 5 * detail.quantity}
            for detail in order_details
            if detail.order.customer and detail.product
        ]
        print(order_data)
        # Tạo danh sách cho likes
        like_data = [
            {'user_id': like.customer.id, 'product_id': like.product.id, 'score': 1}
            for like in likes
            if like.customer and like.product
        ]
        # Kết hợp dữ liệu và tạo DataFrame
        data = order_data + like_data
        df = pd.DataFrame(data)
        print(df)
        # Tạo ma trận người dùng-sản phẩm, tính tổng điểm cho mỗi cặp người dùng và sản phẩm
        user_product_matrix = df.pivot_table(index='user_id', columns='product_id', values='score', aggfunc='sum', fill_value=0)
        print('user_product_matrix')
        print(user_product_matrix)
        # Tính toán độ tương đồng giữa các người dùng
        similarity_matrix = cosine_similarity(user_product_matrix)
        similarity_df = pd.DataFrame(similarity_matrix, index=user_product_matrix.index, columns=user_product_matrix.index)
        print('similarity_matrix')
        print(similarity_matrix)

        print('similarity_df')
        print(similarity_df)

        if customer.is_authenticated and customer.id in user_product_matrix.index:
            #trả về một dictionary predicted_ratings mà khóa là ID sản phẩm và giá trị là rating dự đoán cho từng sản phẩm chưa được đánh giá bởi người dùng này.
            predicted_ratings = predict_ratings(customer.id, user_product_matrix, similarity_df, k=3)
            predicted_ratings_df = pd.DataFrame(list(predicted_ratings.items()), columns=['Product_ID', 'Predicted_Rating'])
            print(predicted_ratings_df)
            filtered_ratings_df = predicted_ratings_df[predicted_ratings_df['Predicted_Rating'] > 0]
            #DataFrame được sắp xếp theo cột Predicted_Rating từ cao xuống thấp
            top_product_ids = filtered_ratings_df.sort_values(by='Predicted_Rating', ascending=False).head(8)['Product_ID']
            print(top_product_ids)
            similar_products = Product.objects.filter(id__in=top_product_ids)
            print(similar_products) 
    else:
        # Tính điểm từ bảng OrderDetail
        orders_scores = OrderDetail.objects.values('product_id').annotate(total_order_score=Sum('quantity') * 5).order_by()
        # Tính điểm từ bảng Like
        likes_scores = Like.objects.values('product_id').annotate(total_like_score=Count('id')).order_by()
        # Biến đổi kết quả thành mảng để dễ dàng truy cập và tính toán
        orders_dict = {item['product_id']: item['total_order_score'] for item in orders_scores}
        likes_dict = {item['product_id']: item['total_like_score'] for item in likes_scores}
        # Kết hợp điểm từ orders và likes
        product_scores = {}
        product_ids = set(orders_dict.keys()).union(set(likes_dict.keys()))
        for pid in product_ids:
            product_scores[pid] = orders_dict.get(pid, 0) + likes_dict.get(pid, 0)
        print("product: ", product_ids)
        print("score: ",product_scores)
        # Sử dụng Case và When tạo annotations cho điểm số trực tiếp trong queryset
        score_cases = [When(id=pid, then=Value(score)) for pid, score in product_scores.items()]
        products_with_scores = Product.objects.filter(id__in=product_ids).annotate(
            score=Case(*score_cases, output_field=IntegerField())
        ).order_by('-score')
        print("products_with_scores: ",products_with_scores)

        # Lấy top sản phẩm có điểm cao nhất
        similar_products = products_with_scores[:8] 
        print("similar_products: ",similar_products)

    # * Chain is used to loop through elements
    for obj in chain(products, sellers, promotions, similar_products):
        obj.discounted_price = calculate_discounted_price(obj)
        obj.is_liked = Like.objects.filter(customer=customer, product=obj).exists() if customer else False

    if request.method == 'POST': 
        productid = request.POST.get('productid')
        productsid = request.POST.get('productsid')
        promotionid = request.POST.get('promotionid')
        
        if productid:
            toggle_like_status(customer, productid)
        elif promotionid:
            toggle_like_status(customer, promotionid)
        else:
            toggle_like_status(customer, productsid)
        
        return redirect(request.path)
    
    request.session['products'] = list(all_products.values()) 
    request.session['categories'] = list(categories.values())
    request.session['samples'] = list(samples_all.values())

    context = {
        'customer': customer,
        'products': products,
        'similar_products': similar_products,
        'promotions': promotions,
        'sellers': sellers,
        'total_items': total_items,
        'categories': categories,
        'samples': samples_all
    }
    
    return render(request, 'app/home.html', context)

def all(request):
    all_products = Product.objects.filter(state=ACTIVE_STATE)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    price_order = request.GET.get('price')

    if min_price and max_price:
        all_products = all_products.filter(price__gte=min_price, price__lte=max_price)

    if price_order == 'asc':
        all_products = sorted(all_products, key=lambda x: calculate_discounted_price(x))
    elif price_order == 'desc':
        all_products = sorted(all_products, key=lambda x: calculate_discounted_price(x), reverse=True)

    paginator = Paginator(all_products, 12)
    page_number = request.GET.get('page', 1)
    products = paginator.get_page(page_number)
    
    previous_page_number = products.previous_page_number() if products.has_previous() else None
    next_page_number = products.next_page_number() if products.has_next() else 2

    customer = request.user if request.user.is_authenticated else None
    cart, items, total_items = get_cart_items(customer)

    for product in products:
        product.discounted_price = calculate_discounted_price(product)
        product.is_liked = Like.objects.filter(customer=customer, product=product).exists() if customer else False

    if request.method == 'POST':
        productsid = request.POST.get('productsid')
        if customer:
            toggle_like_status(customer, productsid)
        
        # Update the URL to include the current page number
        current_page = paginator.page(page_number)
        previous_page_number = current_page.previous_page_number() if current_page.has_previous() else None
        next_page_number = current_page.next_page_number() if current_page.has_next() else 2
        current_url = f"{request.path}?page={page_number}&min_price={min_price}&max_price={max_price}&price={price_order}"

        return redirect(current_url)

    context = {
        'products': products, 
        'total_items': total_items, 
        'samples': _active_samples, 
        'next_page_number': next_page_number,
        'previous_page_number': previous_page_number,
    }
    return render(request, 'app/client/all.html', context)

def rental(request, categories, samples):
    sample_id = samples.strip('/').lower()
    sample_obj = get_object_or_404(Sample.objects.annotate(lower_name=Case(When(name__iexact=sample_id, then=Value(sample_id)), default=Value(''))), lower_name=sample_id)

    customer = request.user if request.user.is_authenticated else None
    cart, items, total_items = get_cart_items(customer)

    all_products = Product.objects.filter(sample_id=sample_obj, state=ACTIVE_STATE)
    paginator = Paginator(all_products, 12)  
    page_number = request.GET.get('page', 1)
    next_page_number = 2
    try:
        products = paginator.page(page_number)
        previous_page_number = products.previous_page_number() if products.has_previous() else None
        next_page_number = products.next_page_number() if products.has_next() else next_page_number
    except EmptyPage:
        products = paginator.page(1)  
        previous_page_number = None
    page_range = list(range(max(1, products.number - 1), min(products.paginator.num_pages, products.number + 1) + 1))
    for product in products:
        product.discounted_price = calculate_discounted_price(product)
        product.is_liked = Like.objects.filter(customer=customer, product=product).exists() if customer else False

    if request.method == 'POST': 
        productsid = request.POST.get('productsid')
        if customer:
            toggle_like_status(customer, productsid)
        return redirect(request.path)
    context = {
        'products': products, 'total_items': total_items, 'samples': _active_samples, 'next_page_number': next_page_number,
        'previous_page_number': previous_page_number, 'page_range': page_range, 'samples_title': sample_obj,
    }
    return render(request, 'app/client/rental.html', context)

def detail(request, categories, samples, productname, productid):
    customer = request.user
    dimensions = Size.objects.all()
    productsgets = Product.objects.filter(id=productid)
    quantities = Quantity.objects.filter(product=productid, state=ACTIVE_STATE)
    # products =  Product.objects...filter(state=ACTIVE_STATE).exclude(id=productid).order_by('?')[:8]

    # Lấy thuộc tính của sản phẩm hiện tại
    current_product = productsgets[0]
    current_product_description = current_product.infor
    current_product_color = current_product.color.name if current_product.color else ""
    current_product_category = current_product.category.name if current_product.category else ""

    # Chuẩn bị thuộc tính về các sản phẩm khác
    all_products = Product.objects.filter(state=ACTIVE_STATE)
    all_products_descriptions = [product.infor for product in all_products]
    all_products_colors = [product.color.name if product.color else "" for product in all_products]
    all_products_categories = [product.category.name if product.category else "" for product in all_products]

    # Kết hợp thông tin và văn bản để vector hóa
    combined_descriptions = [
        f"{description} {color} {category}" 
        for description, color, category in zip(
            all_products_descriptions, all_products_colors, 
            all_products_categories
        )
    ]
    # Vector hóa văn bản và tính toán độ tương tự
    # chuyển đổi văn bản của mỗi sản phẩm thành vector dựa trên tần suất xuất hiện của từng từ, giảm trọng số của những từ 
    # xuất hiện thường xuyên trong tất cả các mô tả (sử dụng TF-IDF).
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(combined_descriptions)
    current_product_vector = vectorizer.transform([f"{current_product_description} {current_product_color} {current_product_category}"])
    similarity_scores = cosine_similarity(current_product_vector, tfidf_matrix)

    # Lấy ra các chỉ số của 8 sản phẩm có sự tương đồng cao nhất (trừ sản phẩm hiện tại)
    similar_product_indices = similarity_scores.argsort()[0][-9:]

    # Lấy thông tin của các sản phẩm tương tự
    products = Product.objects.filter(id__in=similar_product_indices).exclude(id=productid)

    cart, items, total_items = get_cart_items(customer) if customer.is_authenticated else (None, [], 0)
    is_liked = Like.objects.filter(customer=customer, product_id=productid).exists() if customer.is_authenticated else False
    for product in productsgets:
        product.discounted_price = calculate_discounted_price(product)
    for product in products:
        product.discounted_price = calculate_discounted_price(product)
        product.is_liked = Like.objects.filter(customer=customer, product=product).exists() if customer.is_authenticated else False
    if request.method == 'POST': 
        productid = request.POST.get('productid')
        productsid = request.POST.get('productsid')
        if productid:
            toggle_like_status(customer, productid)
        else:
            toggle_like_status(customer, productsid)
        return redirect(request.path)
    context = {
        'productsgets': productsgets, 'total_items': total_items, 'samples': _active_samples, 'products': products, 
        'dimensions': dimensions, 'categories': categories, 'quantities': quantities, 'is_liked': is_liked
    }
    return render(request, 'app/client/detail.html', context)
    
def payment(request):
    customer = request.user
    if not customer.is_authenticated: return redirect('home')
    cart = Cart.objects.get(customer=customer)
    items = CartDetail.objects.filter(cart=cart) if cart else []
    if not items:  return redirect('home')
    total_items = items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_price = sum(
        (item.product.price * (100 - item.product.discount) / 100) * item.quantity 
        for item in items
    ) if len(items) > 0 else 0
    for item in items:
        if item.product.discount == 0:
            item.amount = int(item.product.price * item.quantity)
        else:
            item.amount = int((item.product.price * (100 - item.product.discount) / 100) * item.quantity)
        total_order = int(total_price + 35000)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        total = request.POST.get('total')
        wait_state = State.objects.get(name='Wait')
        order = Order.objects.create(
            customer=customer, phone=phone, address=address, total=total, fee=35000, state=wait_state
        )
        # Duyệt qua từng sản phẩm trong giỏ hàng và tạo đối tượng OrderDetail mới
        for item in items:
            OrderDetail.objects.create(
                order=order, product=item.product, 
                color=item.product.color, size=item.size, 
                quantity=item.quantity, price=item.product.price, 
                discount=item.product.discount, amount=item.amount
            )
            # Quantity.objects.filter(product=item.product, size=item.size).update(quantity=F('quantity') - item.quantity)
            quantity_obj = Quantity.objects.filter(product=item.product, size=item.size).first()
            if quantity_obj and quantity_obj.quantity == item.quantity:
                quantity_obj.state = NO_ACTIVE_STATE
                quantity_obj.save()
            other_users_cart_items = CartDetail.objects.filter(product=item.product, size=item.size).exclude(cart=cart)
            other_users_cart_items.delete()
            for cart_item in other_users_cart_items:
                cart_item.save()
        cart.delete()
        items.delete()
        send_email_order(customer.email, customer.username, [order], order.orderdetail_set.all())
        return redirect('home')
    context = {
        'items': items, 'cart': cart,  'total_items': total_items, 'total_price': total_price, 'total_order': total_order, 'samples': _active_samples
    }
    return render(request, 'app/client/payment.html', context)

def cart(request):
    customer = request.user
    if customer.is_authenticated:
        total_price = 0
        cart, items, total_items = get_cart_items(customer)
        for item in items:
            if item.product.discount == 0:
                item.amount = int(item.product.price * item.quantity)
            else:
                item.amount = int((item.product.price * (100 - item.product.discount) / 100) * item.quantity)
            total_price += item.amount
        total_price = int(total_price)
    else:
        cart, items, total_items, total_price = None, [], 0, 0
    context = {'items': items, 'cart': cart, 'total_items': total_items, 'samples': _active_samples, 'total_price': total_price}
    return render(request, 'app/client/cart.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    sizeId = data['sizeId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id=productId)
    size = Size.objects.get(code=sizeId)
    cart, created = Cart.objects.get_or_create(customer=customer)
    cartItem, created = CartDetail.objects.get_or_create(cart=cart, product=product, size=size, defaults={'quantity': 0})
    
    if cartItem is not None:
        if action == 'add':
            # * Kiểm tra số lượng product còn lại trong dữ liệu Quantity
            available_quantity = Quantity.objects.get(product=product, size=size).quantity
            if available_quantity > cartItem.quantity:
                cartItem.quantity += 1
            else:
                messages.error(request, f'Only {available_quantity} products left!')
        elif action == 'remove': 
            cartItem.quantity -= 1
        elif action == 'delete':
            cartItem.delete()
            return JsonResponse('deleted', safe=False)
        cartItem.save()
        if cartItem.quantity <= 0: 
            cartItem.delete()
        return JsonResponse('added', safe=False)
    else:
        return JsonResponse('error', safe=False)
