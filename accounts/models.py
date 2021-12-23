import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    REQUIRED_FIELDS = []

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)


class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='friend_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self) -> str:
        return f"FriendRequest: ({self.from_user.username} -> {self.to_user.username})"
