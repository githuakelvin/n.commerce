from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm,
    UserProfileForm, AddressForm, PasswordChangeForm
)
from .models import CustomUser, UserProfile, Address


class CustomLoginView(LoginView):
    """Custom login view with better styling."""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to next parameter or home page."""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('products:home')


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = reverse_lazy('products:home')


class UserRegistrationView(CreateView):
    """User registration view."""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('products:home')
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        
        # Log the user in after successful registration
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        
        if user:
            login(self.request, user)
            messages.success(self.request, 'Account created successfully! Welcome to Kenya Commerce.')
            
            # Create user profile
            UserProfile.objects.create(user=user)
        
        return response
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@login_required
def profile_view(request):
    """User profile view."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    addresses = user.addresses.filter(is_active=True)
    
    context = {
        'user': user,
        'profile': profile,
        'addresses': addresses,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit user profile view."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def address_list_view(request):
    """List user addresses."""
    addresses = request.user.addresses.filter(is_active=True)
    
    context = {
        'addresses': addresses,
    }
    
    return render(request, 'accounts/address_list.html', context)


@login_required
def address_create_view(request):
    """Create new address."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
        'title': 'Add New Address',
    }
    
    return render(request, 'accounts/address_form.html', context)


@login_required
def address_edit_view(request, pk):
    """Edit existing address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
        'title': 'Edit Address',
    }
    
    return render(request, 'accounts/address_form.html', context)


@login_required
def address_delete_view(request, pk):
    """Delete address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.is_active = False
        address.save()
        messages.success(request, 'Address deleted successfully!')
        return redirect('accounts:address_list')
    
    context = {
        'address': address,
    }
    
    return render(request, 'accounts/address_confirm_delete.html', context)


@login_required
def password_change_view(request):
    """Change user password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password1']
            
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                
                # Re-authenticate user
                user = authenticate(username=user.username, password=new_password)
                if user:
                    login(request, user)
                
                messages.success(request, 'Password changed successfully!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Current password is incorrect.')
    else:
        form = PasswordChangeForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/password_change.html', context)


@login_required
def order_history_view(request):
    """View user order history."""
    orders = request.user.orders.all().order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'accounts/order_history.html', context)


def terms_and_conditions_view(request):
    """Terms and conditions page."""
    return render(request, 'accounts/terms.html')


def privacy_policy_view(request):
    """Privacy policy page."""
    return render(request, 'accounts/privacy.html')

