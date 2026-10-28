import os
import django
import urllib.request
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Post, Comment

def populate_database():
    print("Clearing old data...")
    Post.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # 1. Accounts with Profile Pics & Specific Bios
    users_info = [
        {
            "username": "tech_gear_hub",
            "bio": "Ultimate Workstation & PC Setups 🖥️⚡ | Tech Reviews & Hardware",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300"
        },
        {
            "username": "nature_explore",
            "bio": "Landscape & Wildlife Photography 🌿🏔️ | Nature Preservationist",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300"
        },
        {
            "username": "study_hustle",
            "bio": "Computer Science Student 📚💻 | Notes, DSA & Exam Preparation",
            "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300"
        },
        {
            "username": "gadget_freak",
            "bio": "Smartphones, Audio Devices & Modern Electronics Unboxing 🎧📱",
            "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300"
        }
    ]

    created_users = []
    for u in users_info:
        user = User.objects.create_user(username=u["username"], email=f"{u['username']}@gmail.com", password="pass123")
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.bio = u["bio"]
        
        # Profile Picture Download
        avatar_temp, _ = urllib.request.urlretrieve(u["avatar"])
        profile.profile_pic.save(f"avatar_{u['username']}.jpg", File(open(avatar_temp, 'rb')))
        profile.save()
        created_users.append(user)

    # 2. Add Follow Connections
    created_users[0].profile.followers.add(created_users[1], created_users[2])
    created_users[1].profile.followers.add(created_users[0])
    created_users[2].profile.followers.add(created_users[0], created_users[3])

    # 3. Categorized Real Posts
    posts_data = [
        {
            "user": created_users[0], # Tech PC Setup
            "caption": "Minimalist Dual Monitor Setup for Software Engineering 💻⚡ Cable management took 3 hours! What do you think?",
            "img_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800"
        },
        {
            "user": created_users[1], # Nature
            "caption": "Misty morning in the northern mountains 🌄 Pure peace and silence away from the city chaos. #nature #photography",
            "img_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800"
        },
        {
            "user": created_users[2], # Study Material
            "caption": "Late night revision session for Operating Systems & Data Structures 📑✍️ Consistency is key! #cs #studymotivation",
            "img_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800"
        },
        {
            "user": created_users[3], # Electronics
            "caption": "Testing out the new active noise-cancelling headphones 🎧 The audio clarity and bass depth are unreal!",
            "img_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"
        },
        {
            "user": created_users[0], # PC Setup
            "caption": "Custom RGB liquid-cooled gaming and rendering rig completed! Specs: RTX 4090 + 64GB RAM 🚀",
            "img_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800"
        }
    ]

    for index, p in enumerate(posts_data):
        post = Post.objects.create(user=p["user"], caption=p["caption"])
        
        # Download Post Image
        img_temp, _ = urllib.request.urlretrieve(p["img_url"])
        post.image.save(f"post_{index}.jpg", File(open(img_temp, 'rb')))
        
        # Add Likes & Comments
        post.likes.add(created_users[(index + 1) % 4], created_users[(index + 2) % 4])
        post.save()

        Comment.objects.create(post=post, user=created_users[(index + 1) % 4], content="Looks super clean and well organized! 🔥")
        Comment.objects.create(post=post, user=created_users[(index + 2) % 4], content="Great quality share! Thanks for posting.")

    print("Database updated successfully with real profile pictures, setups, electronics, nature & study material!")

if __name__ == '__main__':
    populate_database()
