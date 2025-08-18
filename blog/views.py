from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from .models import Post, Category, Comment
from .forms import CommentForm, SearchForm

def blog_list(request):
    posts_list = Post.objects.filter(status='published').order_by('-publish_date')
    
    # Pagination
    paginator = Paginator(posts_list, 6)  # 6 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish_date')[:5]
    
    context = {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/post_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Increment view count
    post.increment_views()
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    
    # Comment form
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(post.get_absolute_url())
    else:
        comment_form = CommentForm()
    
    # Similar posts (by tags)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(status='published', tags__in=post_tags_ids)\
                               .exclude(id=post.id)\
                               .distinct()[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
    }
    return render(request, 'blog/post_detail.html', context)

def blog_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts_list = Post.objects.filter(status='published', category=category).order_by('-publish_date')
    
    # Pagination
    paginator = Paginator(posts_list, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish_date')[:5]
    
    context = {
        'category': category,
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/post_category.html', context)

def blog_tag(request, tag_slug):
    posts_list = Post.objects.filter(status='published', tags__slug=tag_slug).order_by('-publish_date')
    
    # Pagination
    paginator = Paginator(posts_list, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish_date')[:5]
    
    context = {
        'tag': tag_slug,
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/post_tag.html', context)

def blog_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.filter(
                Q(status='published') &
                (Q(title__icontains=query) | 
                 Q(content__icontains=query) |
                 Q(excerpt__icontains=query))
            )
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish_date')[:5]
    
    context = {
        'form': form,
        'query': query,
        'results': results,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/post_search.html', context)