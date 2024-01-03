from django.contrib.auth.models import AbstractUser
from django.db import models

class Friendship(models.Model):
    from_user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='friendship_requests_sent')
    to_user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='friendship_requests_received')
    
    friend_status = models.BooleanField(default=False) 
    request_status = models.BooleanField(default=True)  
    reject_status = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} : {self.friend_status}"

    class Meta:
        unique_together = ('from_user', 'to_user')  
