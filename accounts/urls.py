from django.urls import path

from accounts.api import (
    FriendAPIView,
    FriendRequestAPIView,
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    RegisterAccountAPIView,
    DecoratedTokenVerifyView,
    AccountSelfAPIView,
    AccountAPIView,
)

app_name = 'accounts'
urlpatterns = [
    path('register/', RegisterAccountAPIView.as_view(), name='register'),
    path('token/', DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', DecoratedTokenVerifyView.as_view(), name='token_verify'),
    path('friends/', FriendAPIView.as_view(), name='friends'),
    path('friend-requests/', FriendRequestAPIView.as_view(), name='friend_requests'),
    path('me/', AccountSelfAPIView.as_view(), name='account_self'),
    path('<uuid:pk>/', AccountAPIView.as_view(), name='account_detail'),
]
