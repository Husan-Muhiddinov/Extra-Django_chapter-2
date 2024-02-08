from django.shortcuts import render
from django.contrib.auth.models import User
from .models import ChatGroup
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def index(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "index.html", {"users":users,})






@login_required
def chat(request, username):
    users = User.objects.exclude(id=request.user.id)
    user1 = request.user
    user2 = User.objects.get(username=username)

    chatgroup = ChatGroup.objects.filter(users=user1).filter(users=user2).first()

    if not chatgroup:
        chatgroup = ChatGroup.objects.create(name=f"chat_between_{user1.username}_and_{user2.username}")
        chatgroup.users.add(user1, user2)

    context = {"users":users,  "user":user2, "chatgroup":chatgroup }
    return render(request, "chat.html", context)