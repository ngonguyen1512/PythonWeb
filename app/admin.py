from .models import *
from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

class StateSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = [('active', 'Active'), ('no active', 'No Active')]

class ProductForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[('active', 'Active'), ('no active', 'No Active')], widget=StateSelectWidget)
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'infor': forms.Textarea(attrs={'rows': 10, 'cols': 60, 'style': 'height: 200px;'}),
        }

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'sample', 'image_preview', 'name', 'color', 'discount', 'price', 'state']
    search_fields = ['name']
    readonly_fields = ['image_preview']
    form = ProductForm
    fields = (('category', 'sample'), ('image', 'image_preview'), 'name', 'color', ('discount', 'price'), 'infor', 'state')
    list_filter = [('state', admin.RelatedOnlyFieldListFilter)]

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" width="120" />'.format(url=obj.image.url))
    image_preview.short_description = 'Image Preview'

    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Product, ProductAdmin)

class ColorForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[('active', 'Active'), ('no active', 'No Active')], widget=StateSelectWidget)

class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'state']
    search_fields = ['name']
    form = ColorForm
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Color, ColorAdmin)

class SizeForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[('active', 'Active'), ('no active', 'No Active')], widget=StateSelectWidget)
    class Meta:
        model = Size
        fields = '__all__'

class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'state']
    search_fields = ['name']
    form = SizeForm
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Size, SizeAdmin)

class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'product']
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Like, LikeAdmin)

class CategoryForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[('active', 'Active'), ('no active', 'No Active')], widget=StateSelectWidget)

class CategroyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'state']
    search_fields = ['id', 'name']
    form = CategoryForm
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Category, CategroyAdmin)

class SampleForm(forms.ModelForm):
    state = forms.ChoiceField(choices=[('active', 'Active'), ('no active', 'No Active')], widget=StateSelectWidget)

class SampleAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'name', 'state']
    search_fields = ['category__name', 'name', 'state']
    list_filter = ['category__name']
    form = SampleForm
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Sample, SampleAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer']
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Cart, CartAdmin)

class CartDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'size', 'quantity']
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(CartDetail, CartDetailAdmin)

class StateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['id', 'name']
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(State, StateAdmin)
