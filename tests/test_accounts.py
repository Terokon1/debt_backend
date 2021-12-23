from typing import Optional

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account
from tests.base import DefaultAPITestCase
from tests.factories import AccountFactory, delete_after


class AccountTestCase(DefaultAPITestCase):
    def _credentials_setup_from(self, user: Optional[Account] = None) -> None:
        if not user:
            self.client.credentials()
        else:
            token = RefreshToken.for_user(user).access_token
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def setUp(self) -> None:
        super().setUp()
        self.user = Account.objects.create_user(username='test_user_1', password='test_user_1')
        self._credentials_setup_from(self.user)

    def test_register_user_success(self):
        data = {
            'username': 'some-user-1',
            'password': 'some-user-1-password',
        }

        self._credentials_setup_from()
        response = self.client.post(reverse('accounts:register'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Account.objects.filter(username=data['username']).exists()
        )

        Account.objects.get(username=data['username']).delete()

    def test_register_user_same_username_failure(self):
        data = {
            'username': 'some-user-1',
            'password': 'some-user-1-password',
        }
        data_2 = {'username': data['username'], 'password': 'sesame-password'}

        self._credentials_setup_from()
        response = self.client.post(reverse('accounts:register'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_2 = self.client.post(reverse('accounts:register'), data=data_2)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_self_account_information_success(self):
        self._credentials_setup_from(self.user)

        response = self.client.get(reverse('accounts:account_self'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['id'], str(self.user.id))
        self.assertEqual(response.data['username'], self.user.username)

    def test_account_information_success(self):
        self._credentials_setup_from(self.user)

        user_1 = AccountFactory.create()
        self.user.friends.add(user_1)
        with delete_after(user_1):
            response = self.client.get(reverse('accounts:account_detail', kwargs={'pk': user_1.id}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(response.data['id'], str(user_1.id))
            self.assertEqual(response.data['username'], user_1.username)

    def test_account_information_on_self_success(self):
        self._credentials_setup_from(self.user)

        response = self.client.get(reverse('accounts:account_detail', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], str(self.user.id))
        self.assertEqual(response.data['username'], self.user.username)

    def test_account_information_on_non_friend_failure(self):
        self._credentials_setup_from(self.user)

        user_1 = AccountFactory.create()
        with delete_after(user_1):
            response = self.client.get(reverse('accounts:account_detail', kwargs={'pk': user_1.id}))
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
