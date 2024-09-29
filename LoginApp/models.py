from django.utils import timezone
from django.db import models


# Create your models here.

class newuser(models.Model):
    Username=models.CharField(max_length=100)
    Email1=models.EmailField(max_length=100)
    MobileNumber = models.CharField(max_length=10, blank=True, null=True)
    Password1=models.CharField(max_length=100)
    Password2=models.CharField(max_length=100)
    Forgot_password_token = models.UUIDField(blank=True, null=True)
    Token_created_at = models.DateTimeField(default=timezone.now, blank=True, null=True)

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     forgot_password_token = models.CharField(max_length=200)
#     created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
