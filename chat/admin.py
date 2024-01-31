from django.contrib import admin
from .models import Profile, Message, ChatGroup
# Register your models here.


admin.site.register([Profile, Message, ChatGroup])