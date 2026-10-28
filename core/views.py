from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment
from .forms import RegisterForm, ProfileForm, PostForm, CommentForm

# 1. User Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Automatically create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

# 2. User Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# 3. User Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# 4. Main Feed View
@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'core/feed.html', {'posts': posts, 'comment_form': comment_form})

# 5. Create Post View
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'core/create_post.html', {'form': form})

# 6. Like / Unlike Post View
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

# 7. Add Comment View
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

# 8. Profile View & Edit
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)
    posts = Post.objects.filter(user=profile_user)
    is_following = request.user in profile.followers.all()

    if request.method == 'POST' and request.user == profile_user:
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=username)
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'form': form
    }
    return render(request, 'core/profile.html', context)

# 9. Follow / Unfollow User View
@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile, created = UserProfile.objects.get_or_create(user=target_user)
    
    if request.user != target_user:
        if request.user in target_profile.followers.all():
            target_profile.followers.remove(request.user)
        else:
            target_profile.followers.add(request.user)
            
    return redirect('profile', username=username)
