from django import forms
from .models import ReturnRequest

class ReturnRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnRequest
        fields = ['reason', 'notes','order', 'preferred_refund_method']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about your return'
            }),
            'preferred_refund_method': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'preferred_refund_method': 'Preferred Refund Method',
        }