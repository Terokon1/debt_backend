from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account, FriendRequest
from tests.base import DefaultAPITestCase
from tests.factories import delete_after, FriendRequestFactory, AccountFactory


class FriendRequestTestCase(DefaultAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = Account.objects.create_user(username='test_user_1', password='test_user_1')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_request_send_success(self):
        user_1 = Account.objects.create_user(username='test_user_2', password='test_user_2')
        with delete_after(user_1):
            response = self.client.post(reverse('accounts:friend_requests'), data={'username': 'test_user_2'})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(
                FriendRequest.objects.filter(from_user=self.user, to_user=user_1).exists()
            )

            FriendRequest.objects.get(from_user=self.user, to_user=user_1).delete()

    def test_request_send_to_self_failure(self):
        response = self.client.post(reverse('accounts:friend_requests'), data={'username': self.user.username})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_request_list_success(self):
        requests_to_user = FriendRequestFactory.create_batch(to_user=self.user, size=10)

        friend_requests = list(sorted(
            requests_to_user,
            key=lambda request: request.created_at,
            reverse=True,
        ))

        response = self.client.get(reverse('accounts:friend_requests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_friend_requests = response.data

        self.assertEqual(len(friend_requests), len(data_friend_requests))
        for fr, data_fr in zip(friend_requests, data_friend_requests):
            self.assertEqual(str(fr.id), data_fr['id'])
            self.assertEqual(str(fr.from_user_id), data_fr['from_user']['id'])
            self.assertEqual(str(fr.to_user_id), data_fr['to_user']['id'])

    def test_request_create_second_time_pseudo_success(self):
        user_1 = Account.objects.create_user(username='test_user_2', password='test_user_2')
        with delete_after(user_1):
            response = self.client.post(reverse('accounts:friend_requests'), data={'username': 'test_user_2'})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(
                FriendRequest.objects.filter(from_user=self.user, to_user=user_1).exists()
            )

            # we don't want to show that requests has already sent
            # to be sure that friend request that user sent to another is actually real
            response = self.client.post(reverse('accounts:friend_requests'), data={'username': 'test_user_2'})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_request_create_to_unknown_user_pseudo_success(self):
        response = self.client.post(reverse('accounts:friend_requests'), data={'username': 'UNKNOWN_USER___'})
        # do not show that user is not real
        # to be sure that bad guy cannot bruteforce usernames
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertFalse(
            Account.objects.filter(username='UNKNOWN_USER___').exists()
        )
        self.assertFalse(
            FriendRequest.objects.filter(
                from_user=self.user, to_user__username='UNKNOWN_USER___'
            ).exists()
        )

    def test_request_accept_success(self):
        user_1 = Account.objects.create_user(username='test_user_2', password='test_user_2')
        with delete_after(user_1):
            friend_request = FriendRequestFactory.create(from_user=user_1, to_user=self.user)
            response = self.client.patch(
                reverse('accounts:friend_requests'),
                data={
                    'status': 'accept',
                    'friend_request_id': friend_request.id,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.user.refresh_from_db()
            self.assertIn(user_1, self.user.friends.all())
            self.assertFalse(
                FriendRequest.objects.filter(pk=friend_request.id).exists()
            )

    def test_request_decline_success(self):
        user_1 = Account.objects.create_user(username='test_user_2', password='test_user_2')
        with delete_after(user_1):
            friend_request = FriendRequestFactory.create(from_user=user_1, to_user=self.user)
            response = self.client.patch(
                reverse('accounts:friend_requests'),
                data={
                    'status': 'decline',
                    'friend_request_id': friend_request.id,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.user.refresh_from_db()
            self.assertNotIn(user_1, self.user.friends.all())
            self.assertFalse(
                FriendRequest.objects.filter(pk=friend_request.id).exists()
            )

    def test_request_unknown_status_failure(self):
        user_1 = Account.objects.create_user(username='test_user_2', password='test_user_2')
        with delete_after(user_1):
            friend_request = FriendRequestFactory.create(from_user=user_1, to_user=self.user)
            response = self.client.patch(
                reverse('accounts:friend_requests'),
                data={
                    'status': 'UNKNOWN',
                    'friend_request_id': friend_request.id,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.user.refresh_from_db()
            self.assertNotIn(user_1, self.user.friends.all())
            self.assertTrue(
                FriendRequest.objects.filter(pk=friend_request.id).exists()
            )


class FriendTestCase(DefaultAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = Account.objects.create_user(username='test_user_1', password='test_user_1')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_friend_list_success(self):
        friends = AccountFactory.create_batch(size=10)
        self.user.friends.set(friends)

        friends = list(sorted(friends, key=lambda friend: friend.id))

        response = self.client.get(reverse('accounts:friends'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friends_data = response.data
        friends_data = list(sorted(friends_data, key=lambda friend: friend['id']))

        self.assertEqual(len(friends), len(friends_data))
        for friend, friend_data in zip(friends, friends_data):
            self.assertEqual(str(friend.id), friend_data['id'])
