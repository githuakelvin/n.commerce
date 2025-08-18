from django import forms
from django.core.validators import MinValueValidator
from .models import ShippingZone, PickupPoint

class ShippingZoneForm(forms.ModelForm):
    """Form for creating/updating shipping zones"""
    class Meta:
        model = ShippingZone
        fields = [
            'name', 
            'description', 
            'price', 
            'estimated_delivery_time', 
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PickupPointForm(forms.ModelForm):
    """Form for creating/updating pickup points"""
    class Meta:
        model = PickupPoint
        fields = [
            'name',
            'address',
            'city',
            'postal_code',
            'country',
            'contact_number',
            'operating_hours',
            'is_active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class DeliveryStatusUpdateForm(forms.Form):
    """Form for updating delivery status"""
    status = forms.ChoiceField(
        choices=DeliveryStatus.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes...'
        })
    )