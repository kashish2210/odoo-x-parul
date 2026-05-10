from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count

from .models import CommunityPost, PostLike, PostComment
from .forms import CommunityPostForm, CommentForm


@login_required
def community_list_view(request):
    """Community feed — browse all posts with search, filter, and sort."""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')

    posts = CommunityPost.objects.select_related('user', 'trip').annotate(
        like_count=Count('likes'),
        comment_count=Count('comments'),
    )

    # Search
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        )

    # Filter by category
    if category:
        posts = posts.filter(category=category)

    # Sort
    if sort == 'oldest':
        posts = posts.order_by('created_at')
    elif sort == 'most_liked':
        posts = posts.order_by('-like_count', '-created_at')
    elif sort == 'most_commented':
        posts = posts.order_by('-comment_count', '-created_at')
    else:
        posts = posts.order_by('-created_at')

    # Track which posts the current user has liked
    user_liked_ids = set(
        PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
    )

    return render(request, 'community/list.html', {
        'posts': posts,
        'query': query,
        'category': category,
        'sort': sort,
        'user_liked_ids': user_liked_ids,
        'categories': CommunityPost.CATEGORY_CHOICES,
    })


@login_required
def community_create_view(request):
    """Create a new community post."""
    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post shared with the community!')
            return redirect('community:community_list')
    else:
        form = CommunityPostForm(user=request.user)

    return render(request, 'community/create.html', {
        'form': form,
    })


@login_required
def community_detail_view(request, post_id):
    """View a single post with comments."""
    post = get_object_or_404(
        CommunityPost.objects.select_related('user', 'trip').annotate(
            like_count=Count('likes'),
        ),
        id=post_id
    )
    comments = post.comments.select_related('user').order_by('created_at')
    user_has_liked = PostLike.objects.filter(user=request.user, post=post).exists()

    # Handle comment submission
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('community:community_detail', post_id=post.id)
    else:
        comment_form = CommentForm()

    return render(request, 'community/detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
    })


@login_required
def community_like_view(request, post_id):
    """Toggle like on a post."""
    post = get_object_or_404(CommunityPost, id=post_id)
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()

    # Redirect back to where the user came from
    next_url = request.GET.get('next', 'community:community_list')
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect(next_url)


@login_required
def community_delete_view(request, post_id):
    """Delete own post."""
    post = get_object_or_404(CommunityPost, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('community:community_list')
