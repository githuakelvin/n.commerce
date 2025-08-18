from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count
from .models import (
    Category, Brand, Product, ProductImage, ProductReview, 
    Cart, CartItem, Wishlist, ProductSpecification
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    
    list_display = ('name', 'slug', 'products_count', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def products_count(self, obj):
        """Display the count of products in this category."""
        count = obj.get_products_count()
        return format_html('<span style="color: #007cba; font-weight: bold;">{}</span>', count)
    products_count.short_description = 'Products Count'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin interface for Brand model."""
    
    list_display = ('name', 'slug', 'products_count', 'website', 'is_active', 'display_order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'logo', 'website')
        }),
        ('Display Options', {
            'fields': ('is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def products_count(self, obj):
        """Display the count of products for this brand."""
        count = obj.products.count()
        return format_html('<span style="color: #007cba; font-weight: bold;">{}</span>', count)
    products_count.short_description = 'Products Count'


class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImage."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'display_order')


class ProductSpecificationInline(admin.TabularInline):
    """Inline admin for ProductSpecification."""
    model = ProductSpecification
    extra = 1
    fields = ('name', 'value', 'display_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    
    list_display = (
        'name', 'category', 'brand', 'price', 'stock_quantity', 
        'is_active', 'is_featured', 'view_count', 'sold_count'
    )
    list_filter = (
        'category', 'brand', 'is_active', 'is_featured', 'is_bestseller', 
        'is_new_arrival', 'track_inventory', 'created_at'
    )
    search_fields = ('name', 'sku', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'brand', 'tags')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_inventory')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'dimensions', 'color', 'size'),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'is_featured', 'is_bestseller', 'is_new_arrival')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'sold_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'view_count', 'sold_count')
    inlines = [ProductImageInline, ProductSpecificationInline]
    
    def get_queryset(self, request):
        """Custom queryset with select_related for better performance."""
        return super().get_queryset(request).select_related('category', 'brand')
    
    def get_discount_display(self, obj):
        """Display discount percentage."""
        discount = obj.get_discount_percentage()
        if discount > 0:
            return format_html('<span style="color: #28a745; font-weight: bold;">{}% OFF</span>', discount)
        return '-'
    get_discount_display.short_description = 'Discount'
    
    def stock_status(self, obj):
        """Display stock status with color coding."""
        if not obj.track_inventory:
            return format_html('<span style="color: #6c757d;">Not Tracked</span>')
        
        if obj.stock_quantity == 0:
            return format_html('<span style="color: #dc3545; font-weight: bold;">Out of Stock</span>')
        elif obj.is_low_stock():
            return format_html('<span style="color: #ffc107; font-weight: bold;">Low Stock ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: #28a745;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock Status'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin interface for ProductImage model."""
    
    list_display = ('product', 'image_preview', 'is_main', 'display_order', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('product__name', 'alt_text')
    ordering = ('product', 'is_main', 'display_order')
    
    fieldsets = (
        ('Image Information', {
            'fields': ('product', 'image', 'alt_text')
        }),
        ('Display Options', {
            'fields': ('is_main', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def image_preview(self, obj):
        """Display image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return 'No Image'
    image_preview.short_description = 'Preview'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin interface for ProductReview model."""
    
    list_display = ('product', 'user', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_verified_purchase')
        }),
        ('Votes', {
            'fields': ('helpful_votes', 'total_votes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'helpful_votes', 'total_votes')
    
    def get_queryset(self, request):
        """Custom queryset with select_related for better performance."""
        return super().get_queryset(request).select_related('product', 'user')
    
    def helpful_percentage(self, obj):
        """Display helpful percentage."""
        percentage = obj.get_helpful_percentage()
        return f"{percentage}%"
    helpful_percentage.short_description = 'Helpful %'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart model."""
    
    list_display = ('id', 'user', 'session_key', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'session_key')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'session_key')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def total_items(self, obj):
        """Display total items in cart."""
        return obj.get_total_items()
    total_items.short_description = 'Total Items'
    
    def total_price(self, obj):
        """Display total price of cart."""
        return f"KES {obj.get_total_price():,.2f}"
    total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for CartItem model."""
    
    list_display = ('cart', 'product', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__username', 'product__name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Item Information', {
            'fields': ('cart', 'product', 'quantity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def unit_price(self, obj):
        """Display unit price."""
        return f"KES {obj.product.price:,.2f}"
    unit_price.short_description = 'Unit Price'
    
    def total_price(self, obj):
        """Display total price for this item."""
        return f"KES {obj.get_total_price():,.2f}"
    total_price.short_description = 'Total Price'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin interface for Wishlist model."""
    
    list_display = ('user', 'product', 'product_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Wishlist Information', {
            'fields': ('user', 'product')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def product_price(self, obj):
        """Display product price."""
        return f"KES {obj.product.price:,.2f}"
    product_price.short_description = 'Product Price'


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """Admin interface for ProductSpecification model."""
    
    list_display = ('product', 'name', 'value', 'display_order')
    list_filter = ('display_order',)
    search_fields = ('product__name', 'name', 'value')
    ordering = ('product', 'display_order')
    
    fieldsets = (
        ('Specification Information', {
            'fields': ('product', 'name', 'value', 'display_order')
        }),
    )


