from accounts.api.friend_requests import FriendRequestAPIView
from accounts.api.friends import FriendAPIView
from accounts.api.tokens import (
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    DecoratedTokenVerifyView,
)
from accounts.api.accounts import (
    RegisterAccountAPIView,
    AccountSelfAPIView,
    AccountAPIView,
)
