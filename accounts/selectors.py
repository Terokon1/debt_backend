from django.db.models import QuerySet, Q

from accounts.models import Account, FriendRequest


def get_all_friend_requests(user: Account) -> QuerySet[FriendRequest]:
    return FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )


def get_friend_requests_to_accept(user: Account) -> QuerySet[FriendRequest]:
    return user.friend_requests.order_by('-created_at')
