from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import PostForm, CommentForm


def home(request):
    """Home page view showing published posts"""
    posts = Post.objects.filter(is_published=True)
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj,
    }
    return render(request, 'myapp/home.html', context)


def post_detail(request, pk):
    """Detail view for a single post"""
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'myapp/post_detail.html', context)


@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    context = {'form': form}
    return render(request, 'myapp/create_post.html', context)


@login_required
def edit_post(request, pk):
    """Edit an existing post"""
    post = get_object_or_404(Post, pk=pk)
    
    # Only allow the author to edit their post
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    context = {'form': form, 'post': post}
    return render(request, 'myapp/edit_post.html', context)


@login_required
def my_posts(request):
    """View for user's own posts"""
    posts = Post.objects.filter(author=request.user)
    context = {'posts': posts}
    return render(request, 'myapp/my_posts.html', context)


