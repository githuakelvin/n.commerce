from django import forms
from .models import Comment, Post
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'content')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'excerpt', 'featured_image', 'category', 'status', 'publish_date', 'tags')
        widgets = {
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)