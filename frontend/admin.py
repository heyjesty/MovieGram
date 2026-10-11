from django.contrib import admin

from frontend.models import CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "user", "full_name", "total", "created_at"]
    inlines = [OrderItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "added_at"]
