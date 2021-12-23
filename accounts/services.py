from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts import constants
from accounts.errors import AlreadyFriendsError, WrongUserError
from accounts.models import Account, FriendRequest


class CreateFriendRequestService:
    def __init__(self, from_user: Account, to_username: str):
        self.from_user = from_user
        self.to_username = to_username

    def create_request(self):
        to_user = self._get_user_from_username(self.to_username)
        self._validate_already_friends(self.from_user, to_user)
        return FriendRequest.objects.get_or_create(
            from_user=self.from_user,
            to_user=to_user,
        )

    @staticmethod
    def _get_user_from_username(username: str) -> Account:
        return Account.objects.get(username=username)

    @staticmethod
    def _validate_already_friends(
            user_1: Account,
            user_2: Account,
    ) -> None:
        if user_1.friends.filter(pk=user_2.pk).exists():
            raise AlreadyFriendsError

    def _validate_creator_is_not_same_with_username(self):
        if self.from_user.username == self.to_username:
            raise ValidationError("Trying to be friend with self.")


class UpdateFriendRequestService:
    def __init__(self, friend_request_id: str, status: str, user: Account):
        self.friend_request = FriendRequest.objects.get(
            pk=friend_request_id,
        )
        self.status = status
        self.user = user

    def update_friend_request(self):
        self._validate_request_to_user()
        if self.status == constants.STATUS_ACCEPT:
            self._accept_friend_request()
        elif self.status == constants.STATUS_DECLINE:
            self._decline_friend_request()
        else:
            raise ValidationError("Status unknown")

    def _validate_request_to_user(self) -> None:
        if self.friend_request.to_user != self.user:
            raise WrongUserError

    def _accept_friend_request(self):
        from_user = self.friend_request.from_user
        with transaction.atomic():
            self.user.friends.add(from_user)
            self.friend_request.delete()

    def _decline_friend_request(self):
        self.friend_request.delete()
