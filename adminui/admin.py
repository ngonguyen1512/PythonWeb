from app.models import *
from django import forms
from django.urls import reverse
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

class CreateUserFormAdd(UserCreationForm):
    first_name = forms.CharField(label='First Name', max_length=30, required=False)
    last_name = forms.CharField(label='Last Name', max_length=30, required=False)
    is_staff = forms.BooleanField(label='Is Staff', required=False)

    def __init__(self, *args, **kwargs):
        super(CreateUserFormAdd, self).__init__(*args, **kwargs)
        if self.user_is_manager:
            if 'groups' in self.fields:
                self.fields['groups'].queryset = Group.objects.filter(name__in=['staff', 'shipper'])
        if self.user_is_admin:
            if 'groups' in self.fields:
                self.fields['groups'].queryset = Group.objects.filter(name__in=['manager', 'staff', 'shipper'])

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'groups']

class CreateUserFormEdit(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserFormEdit, self).__init__(*args, **kwargs)
        if self.user_is_manager:
            if 'groups' in self.fields:
                self.fields['groups'].queryset = Group.objects.filter(name__in=['staff', 'shipper'])
        if self.user_is_admin:
            if 'groups' in self.fields:
                self.fields['groups'].queryset = Group.objects.filter(name__in=['manager', 'staff', 'shipper'])

    class Meta:
        model = get_user_model()
        fields = ['groups']

    def save(self, commit=True):
        user = super(CreateUserFormEdit, self).save(commit=False)
        if hasattr(self, 'user_is_manager') and self.user_is_manager:
            user.is_staff = True
        if commit:
            user.save()
        return user
    
class CustomUserAdmin(BaseUserAdmin):
    add_form = CreateUserFormAdd
    form = CreateUserFormEdit

    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    list_filter = ('is_staff', 'groups')
    fieldsets = ((None, {'fields': ('groups',)}),)
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('username', ('first_name', 'last_name'), 'email', ('password1', 'password2'), 'is_staff', 'groups'),
    }),)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('id',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user_is_manager = request.user.groups.filter(name='manager').exists()
        form.user_is_admin = request.user.groups.filter(name='admin').exists()
        return form

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user.groups.filter(name='manager').exists():
                if not obj.is_staff or not obj.groups.filter(name__in=['staff', 'shipper']).exists():
                    messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
                    return False
            elif request.user.groups.filter(name='admin').exists():
                if not obj.is_staff:
                    messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
                    return False
        return super().has_change_permission(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and request.user.groups.filter(name='manager').exists() and not obj.groups.filter(name__in=['staff', 'shipper']).exists():
            messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
            return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
        if obj and request.user.groups.filter(name='admin').exists() and not obj.groups.filter(name__in=['manager', 'staff', 'shipper']).exists():
            messages.error(request, "Bạn không có quyền chỉnh sửa người dùng này.")
            return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
        return super().change_view(request, object_id, form_url, extra_context)

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    def has_delete_permission(self, request, obj=None):
        if request.user.groups.filter(name='manager').exists() and obj and obj.groups.filter(name__in=['staff', 'shipper']).exists():
            return

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class OrderAdminForm(forms.ModelForm):
    explanation = forms.CharField(label='Explanation', max_length=255, required=False)
    
    class Meta:
        model = Order
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OrderAdminForm, self).__init__(*args, **kwargs)   
        if self.request.user.groups.filter(name__in=['admin', 'manager', 'staff']).exists():
            if 'accept' in self.fields:
                self.fields['accept'].queryset = get_user_model().objects.filter(username=self.request.user.username)
                self.fields['accept'].initial = get_user_model().objects.get(username=self.request.user.username)
            if 'shipper' in self.fields:
                self.fields['shipper'].queryset = get_user_model().objects.filter(groups__name='shipper')
            if 'state' in self.fields:
                self.fields['state'].queryset = State.objects.filter(name__in=['Cancel', 'Delivery'])
        
        if self.request.user.groups.filter(name='shipper').exists():
            if 'accept' in self.fields:
                self.fields['accept'].queryset = get_user_model().objects.exclude(groups__name='shipper')
            if 'shipper' in self.fields:
                self.fields['shipper'].queryset = get_user_model().objects.filter(groups__name='shipper')  
            if 'state' in self.fields:
                self.fields['state'].queryset = State.objects.filter(name__in=['Done', 'Unsuccessful'])
    def clean(self):
        cleaned_data = super().clean()
        for field in self.fields:
            if field not in ['accept', 'shipper', 'state', 'explanation']:
                cleaned_data[field] = getattr(self.instance, field)
        return cleaned_data

class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ['id', 'date', 'customer', 'phone', 'address', 'fee', 'total', 'accept', 'shipper', 'state', 'explanation']
    search_fields = ['customer__username', 'phone']
    list_filter = [('state', admin.RelatedOnlyFieldListFilter)]

    def get_form(self, request, obj=None, **kwargs):
        # Gọi phương thức get_form của class cha (class ModelAdmin) => Tạo ra form mặc định cho model.
        form = super().get_form(request, obj, **kwargs) 
        form.user_is = request.user.groups.filter(name__in=['admin', 'manager', 'staff']).exists()
        form.user_is_shipper = request.user.groups.filter(name='shipper').exists()
        form.request = request
        return form
    
    def has_change_permission(self, request, obj=None):
        return obj and str(obj.state) not in ['Cancel', 'Unsuccessful', 'Done'] 
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='shipper').exists():
            queryset = queryset.filter(state__name='Delivery')
        return queryset
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.shipper = form.cleaned_data['shipper']
            obj.state = form.cleaned_data['state']
            obj.explanation = form.cleaned_data['explanation']

            if form.user_is_shipper:
                obj.accept = form.cleaned_data['accept']
         
        for field in form.fields:
            if field not in ['shipper', 'state', 'accept', 'explanation']:
                setattr(obj, field, form.cleaned_data[field])

        if str(obj.state) in ['Unsuccessful', 'Cancel'] and not obj.explanation:
            messages.error(request, 'Explanation is required for Unsuccessful or Cancel state.')
            return
        
        super().save_model(request, obj, form, change)

        if str(obj.state) == 'Delivery':
            self.update_quantity(obj, decrease=True)
        elif str(obj.state) == 'Unsuccessful':
            self.update_quantity(obj, decrease=False)

    def update_quantity(self, obj, decrease=True):
        items = OrderDetail.objects.filter(order=obj)
        for item in items:
            quantity_obj = Quantity.objects.filter(product=item.product, size=item.size).first()
            if quantity_obj:
                if decrease:
                    quantity_obj.quantity -= item.quantity
                else:
                    quantity_obj.quantity += item.quantity

                # quantity_obj.state = 'No active' if quantity_obj.quantity == 0 else 'Active'
                quantity_obj.save()
    # Override phương thức save_related để không lưu các formset liên quan
    def save_related(self, request, form, formsets, change):
        pass

admin.site.register(Order, OrderAdmin)

class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'color', 'size', 'quantity','amount']
    search_fields = ['order__id', 'product__name']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='shipper').exists():
            queryset = queryset.filter(order__state__name='Delivery')
        return queryset

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def product_id(self, obj):
        return obj.product.id  

    product_id.short_description = 'Product ID'

admin.site.register(OrderDetail, OrderDetailAdmin)

class StateSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [('active', 'Active'), ('no active', 'No Active')]

class QuantityForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[('active', 'Active'), ('no active', 'No Active')], widget=StateSelectWidget)

class QuantityAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'size', 'quantity', 'state']
    search_fields = ['product__name']
    list_filter = ['product__name', 'state__name']
    fields = (('product','state'), ('size','quantity'))
    form = QuantityForm
    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['admin', 'manager']).exists()

    def has_delete_permission(self, request, obj=None):
        return obj and obj.quantity == 0

    def delete_model(self, request, obj):
        if obj.quantity == 0:
            super().delete_model(request, obj)
        else:
            messages.error(request, "Số lượng phải bằng 0 để xóa.")
    
admin.site.register(Quantity, QuantityAdmin)