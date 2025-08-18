from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog posts
    path('', views.blog_list, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Categories
    path('category/<slug:slug>/', views.blog_category, name='blog_category'),
    
    # Tags
    path('tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),
    
    # Search
    path('search/', views.blog_search, name='blog_search'),
]

