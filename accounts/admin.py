from django.contrib import admin

from accounts.models import FriendRequest, Account

admin.site.register(FriendRequest)
admin.site.register(Account)
