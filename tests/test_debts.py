from unittest import mock

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Account
from debts.models import DebtRequest, Debt
from tests.base import DefaultAPITestCase
from tests.factories import (
    AccountFactory,
    DebtFactory,
    DebtRequestFactory,
    delete_after,
)


class DebtTestCase(DefaultAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = Account.objects.create_user(username='test_user_1', password='test_user_1')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_list_of_debts_success(self):
        debts_as_debtor = DebtFactory.create_batch(debtor=self.user, size=10)
        debts_as_creditor = DebtFactory.create_batch(creditor=self.user, size=10)

        debts = list(sorted(
            (*debts_as_debtor, *debts_as_creditor),
            key=lambda debt: debt.created,
            reverse=True,
        ))

        response = self.client.get(reverse('debts:debts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        debts_data = response.data

        self.assertEqual(len(debts), len(debts_data))
        for debt, debt_data in zip(debts, debts_data):
            self.assertEqual(str(debt.id), debt_data['id'])
            self.assertEqual(str(debt.money), debt_data['money'])
            self.assertEqual(str(debt.creditor_id), debt_data['creditor']['id'])
            self.assertEqual(str(debt.debtor_id), debt_data['debtor']['id'])


class DebtRequestTestCase(DefaultAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = Account.objects.create_user(username='test_user_1', password='test_user_1')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_create_debt_request_success(self):
        user_1 = AccountFactory.create()
        self.user.friends.add(user_1)

        with delete_after(user_1):
            response = self.client.post(
                reverse('debts:debts_requests'),
                data={
                    "money": "1200",
                    "creditor_id": self.user.id,
                    "debtor_id": user_1.id,
                    "description": "description",
                },
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            debt_request_user_is_creditor = DebtRequest.objects.filter(creditor=self.user, debtor=user_1)
            self.assertTrue(debt_request_user_is_creditor.exists())
            debt_request_user_is_creditor.delete()

            response = self.client.post(
                reverse('debts:debts_requests'),
                data={
                    "money": "1200",
                    "creditor_id": user_1.id,
                    "debtor_id": self.user.id,
                    "description": "description",
                })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            debt_request_user_is_debtor = DebtRequest.objects.filter(debtor=self.user, creditor=user_1)
            self.assertTrue(debt_request_user_is_debtor.exists())
            debt_request_user_is_debtor.delete()

    def test_create_debt_request_from_another_user_failure(self):
        user_1 = AccountFactory.create()
        self.user.friends.add(user_1)

        user_2 = AccountFactory.create()
        user_2.friends.add(user_1)

        with delete_after(user_1), delete_after(user_2):
            response = self.client.post(
                reverse('debts:debts_requests'),
                data={
                    "money": "1200",
                    "creditor_id": user_1.id,
                    "debtor_id": user_2.id,
                    "description": "description",
                },
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debt_request_not_in_friends_failure(self):
        user_1 = AccountFactory.create()

        with delete_after(user_1):
            response = self.client.post(
                reverse('debts:debts_requests'),
                data={
                    "money": "1200",
                    "creditor_id": user_1.id,
                    "debtor_id": self.user.id,
                    "description": "description",
                },
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_debt_request_to_self_failure(self):
        response = self.client.post(
            reverse('debts:debts_requests'),
            data={
                "money": "1200",
                "creditor_id": self.user.id,
                "debtor_id": self.user.id,
                "description": "description",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_debt_requests_success(self):
        creditor_debt_requests = DebtRequestFactory.create_batch(
            creditor=self.user,
            creator=self.user,
            size=10,
        )
        debtor_debt_requests = DebtRequestFactory.create_batch(
            debtor=self.user,
            creator=self.user,
            size=10,
        )

        debt_requests = list(
            sorted(
                (*creditor_debt_requests, *debtor_debt_requests),
                key=lambda debt_request: debt_request.created,
                reverse=True,
            )
        )
        response = self.client.get(reverse('debts:debts_requests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        debt_requests_data = response.data
        self.assertEqual(len(debt_requests), len(debt_requests_data))
        for dr, dr_data in zip(debt_requests, debt_requests_data):
            self.assertEqual(str(dr.id), dr_data['id'])
            self.assertEqual(str(dr.money), dr_data['money'])
            self.assertEqual(str(dr.creditor_id), dr_data['creditor']['id'])
            self.assertEqual(str(dr.debtor_id), dr_data['debtor']['id'])

    def test_list_debt_requests_with_used_debts_success(self):
        creditor_debt_requests = DebtRequestFactory.create_batch(
            creditor=self.user,
            creator=self.user,
            size=10,
        )
        debtor_debt_requests = DebtRequestFactory.create_batch(
            debtor=self.user,
            creator=self.user,
            size=10,
        )
        debt_requests = list(
            sorted(
                (*creditor_debt_requests, *debtor_debt_requests),
                key=lambda debt_request: debt_request.created,
                reverse=True,
            )
        )

        used_debt_requests = DebtRequestFactory.create_batch(
            debtor=self.user,
            creator=self.user,
            size=5
        )
        for used_debt_request in used_debt_requests:
            Debt.create_from_request(used_debt_request)
            self.assertFalse(used_debt_request.is_active)

        declined_debt_requests = DebtRequestFactory.create_batch(
            creditor=self.user,
            creator=self.user,
            size=5,
            declined=True,
        )
        for declined_debt_request in declined_debt_requests:
            self.assertFalse(declined_debt_request.is_active)

        bad_debt_requests = [*used_debt_requests, *declined_debt_requests]

        response = self.client.get(reverse('debts:debts_requests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        debt_requests_data = response.data
        debt_requests_data_ids = [debt_data['id'] for debt_data in debt_requests_data]

        bad_debt_requests_ids = [used_debt_request.id for used_debt_request in bad_debt_requests]
        for bad_debt_request_id in bad_debt_requests_ids:
            self.assertNotIn(bad_debt_request_id, debt_requests_data_ids)

        self.assertEqual(len(debt_requests), len(debt_requests_data))
        for dr, dr_data in zip(debt_requests, debt_requests_data):
            self.assertEqual(str(dr.id), dr_data['id'])
            self.assertEqual(str(dr.money), dr_data['money'])
            self.assertEqual(str(dr.creditor_id), dr_data['creditor']['id'])
            self.assertEqual(str(dr.debtor_id), dr_data['debtor']['id'])

    def test_accept_debt_request_success(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=user_1,
                creditor=user_1,
                debtor=self.user,
            )
            response = self.client.patch(
                reverse('debts:debts_requests'),
                data={
                    'debt_request_id': debt_request.id,
                    'status': 'accept',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            debt = Debt.objects.filter(
                creditor=user_1,
                debtor=self.user,
            )
            self.assertTrue(debt.exists())
            debt = debt.first()
            self.assertEqual(str(debt.id), response.data['id'])

            self.assertFalse(
                DebtRequest.objects.get(pk=debt_request.id).is_active
            )

    def test_accept_inactive_debt_request_failure(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=user_1,
                creditor=user_1,
                debtor=self.user,
                declined=True,
            )
            self.assertFalse(debt_request.is_active)
            response = self.client.patch(
                reverse('debts:debts_requests'),
                data={
                    'debt_request_id': debt_request.id,
                    'status': 'accept',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertFalse(
                Debt.objects.filter(
                    creditor=user_1,
                    debtor=self.user,
                ).exists()
            )

    def test_decline_debt_request_success(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=user_1,
                creditor=user_1,
                debtor=self.user,
            )
            response = self.client.patch(
                reverse('debts:debts_requests'),
                data={
                    'debt_request_id': debt_request.id,
                    'status': 'decline',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            debt = Debt.objects.filter(
                creditor=user_1,
                debtor=self.user,
            )
            self.assertFalse(debt.exists())

            self.assertFalse(
                DebtRequest.objects.get(pk=debt_request.id).is_active
            )

    def test_change_debt_request_status_unknown_failure(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=user_1,
                creditor=user_1,
                debtor=self.user,
            )
            response = self.client.patch(
                reverse('debts:debts_requests'),
                data={
                    'debt_request_id': debt_request.id,
                    'status': 'UNKNOWN###___',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertTrue(
                DebtRequest.objects.filter(pk=debt_request.id).exists()
            )

    def test_accept_debt_request_from_creator_failure(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=self.user,
                creditor=user_1,
                debtor=self.user,
            )
            response = self.client.patch(
                reverse('debts:debts_requests'),
                data={
                    'debt_request_id': debt_request.id,
                    'status': 'accept',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_debt_request_from_another_user_failure(self):
        user_1 = AccountFactory.create()
        user_2 = AccountFactory.create()
        with delete_after(user_1), delete_after(user_2):
            debt_request = DebtRequestFactory.create(
                creator=user_2,
                creditor=user_1,
                debtor=user_1,
            )
            response = self.client.patch(
                reverse('debts:debts_requests'),
                data={
                    'debt_request_id': debt_request.id,
                    'status': 'accept',
                },
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notify_request_created_success(self):
        user_1 = AccountFactory.create()
        self.user.friends.add(user_1)

        with delete_after(user_1):
            with self.restore_signals(), \
                    mock.patch('redis_utils.send_to_pub') as mocked_send_to_pub:
                response = self.client.post(
                    reverse('debts:debts_requests'),
                    data={
                        "money": "1200",
                        "creditor_id": self.user.id,
                        "debtor_id": user_1.id,
                        "description": "description",
                    },
                )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            self.assertTrue(mocked_send_to_pub.called)
            events = mocked_send_to_pub.call_args_list[0][0][0]

            self.assertEqual(len(events), 1)
            event_created = events[0]
            self.assertEqual(event_created.user_id, user_1.id)
            self.assertEqual(event_created.data['event'], 'created')
            self.assertEqual(event_created.data['type'], 'DebtRequest')
            self.assertEqual(event_created.data['object']['money'], '1200.00')

            debt_request = DebtRequest.objects.get(creditor=self.user, debtor=user_1)
            self.assertEqual(event_created.data['object']['id'], str(debt_request.id))

    def test_notify_accepted_debt_request_creator_success(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=user_1,
                creditor=user_1,
                debtor=self.user,
            )
            with self.restore_signals(), mock.patch('redis_utils.send_to_pub') as mocked_send_to_pub:
                response = self.client.patch(
                    reverse('debts:debts_requests'),
                    data={
                        'debt_request_id': debt_request.id,
                        'status': 'accept',
                    },
                )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertTrue(mocked_send_to_pub.called)
            events = mocked_send_to_pub.call_args_list[0][0][0]

            self.assertEqual(len(events), 1)
            event_debt_request_updated = events[0]
            self.assertEqual(event_debt_request_updated.user_id, str(user_1.id))
            self.assertEqual(event_debt_request_updated.data['event'], 'status_updated')
            self.assertEqual(event_debt_request_updated.data['type'], 'DebtRequest')
            self.assertEqual(event_debt_request_updated.data['status'], 'accept')

            debt_request = DebtRequest.objects.get(debtor=self.user, creditor=user_1)
            self.assertEqual(event_debt_request_updated.data['object']['id'], str(debt_request.id))
            self.assertEqual(event_debt_request_updated.data['object']['money'], str(debt_request.money))
            self.assertEqual(event_debt_request_updated.data['object']['is_active'], debt_request.is_active)

    def test_notify_declined_debt_request_creator_success(self):
        user_1 = AccountFactory.create()
        with delete_after(user_1):
            debt_request = DebtRequestFactory.create(
                creator=user_1,
                creditor=user_1,
                debtor=self.user,
            )
            with self.restore_signals(), mock.patch('redis_utils.send_to_pub') as mocked_send_to_pub:
                response = self.client.patch(
                    reverse('debts:debts_requests'),
                    data={
                        'debt_request_id': debt_request.id,
                        'status': 'decline',
                    },
                )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            self.assertTrue(mocked_send_to_pub.called)
            events = mocked_send_to_pub.call_args_list[0][0][0]

            self.assertEqual(len(events), 1)
            event_debt_request_updated = events[0]
            self.assertEqual(event_debt_request_updated.user_id, str(user_1.id))
            self.assertEqual(event_debt_request_updated.data['event'], 'status_updated')
            self.assertEqual(event_debt_request_updated.data['type'], 'DebtRequest')
            self.assertEqual(event_debt_request_updated.data['status'], 'decline')

            debt_request = DebtRequest.objects.get(debtor=self.user, creditor=user_1)
            self.assertEqual(event_debt_request_updated.data['object']['id'], str(debt_request.id))
            self.assertEqual(event_debt_request_updated.data['object']['money'], str(debt_request.money))
            self.assertEqual(event_debt_request_updated.data['object']['is_active'], debt_request.is_active)
