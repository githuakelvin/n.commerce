from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
import uuid

User = get_user_model()

class Category(models.Model):
    """Product category model."""
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Display options
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the absolute URL for the category."""
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    def get_products_count(self):
        """Get the count of active products in this category."""
        return self.products.filter(is_active=True).count()


class Brand(models.Model):
    """Product brand model."""
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True)
    
    # Display options
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the absolute URL for the brand."""
        return reverse('products:brand_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Product model."""
    
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    description = RichTextField()
    short_description = models.TextField(max_length=500, blank=True)
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    tags = TaggableManager(blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    track_inventory = models.BooleanField(default=True)
    
    # Physical attributes
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text='Weight in kg')
    dimensions = models.CharField(max_length=100, blank=True, help_text='L x W x H in cm')
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and SKU if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get the absolute URL for the product."""
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    def get_discount_percentage(self):
        """Calculate discount percentage if compare price exists."""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0
    
    def is_low_stock(self):
        """Check if product is running low on stock."""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold
    
    def get_main_image(self):
        """Get the main product image."""
        main_image = self.images.filter(is_main=True).first()
        if main_image:
            return main_image.image
        # Return first image if no main image
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return None
    
    def increment_view_count(self):
        """Increment the view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ProductImage(models.Model):
    """Product image model."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['is_main', 'display_order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Ensure only one main image per product."""
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    """Product review model."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Review content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5'
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    
    # Helpful votes
    helpful_votes = models.PositiveIntegerField(default=0)
    total_votes = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
    
    def get_helpful_percentage(self):
        """Calculate helpful percentage."""
        if self.total_votes == 0:
            return 0
        return int((self.helpful_votes / self.total_votes) * 100)


class Cart(models.Model):
    """Shopping cart model."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart {self.id}"
    
    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self):
        """Get total price of items in cart."""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_cart_items(self):
        """Get all cart items."""
        return self.items.all()
    
    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """Cart item model."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in cart"
    
    def get_total_price(self):
        """Get total price for this item."""
        return self.product.price * self.quantity
    
    def save(self, *args, **kwargs):
        """Ensure quantity doesn't exceed stock."""
        if self.product.track_inventory and self.quantity > self.product.stock_quantity:
            self.quantity = self.product.stock_quantity
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """User wishlist model."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} in {self.user.username}'s wishlist"


class ProductSpecification(models.Model):
    """Product specification model."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Product Specification'
        verbose_name_plural = 'Product Specifications'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.name}: {self.value} for {self.product.name}"



