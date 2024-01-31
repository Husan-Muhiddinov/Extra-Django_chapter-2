from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.


class ChatGroup(models.Model):
    name = models.CharField(max_length=250)
    users = models.ManyToManyField(User)

    def __str__(self):
        return str(self.name)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    chatgroup = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    body = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.body)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    # bitta odamga bitta profil
    status = models.CharField(default='offline', max_length=150)  #
    picture = models.ImageField(upload_to="profile_images/", default="default.png")

    def __str__(self):
        return str(f"Profile of {self.user.username}")


### Har bitta user yaratilganda Profile ham yaratilishi kerak shuning uchun signaldan foydalanamiz   #####

@receiver(sender=User, signal=post_save)
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)