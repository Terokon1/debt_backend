import uuid
from typing import Optional

from rest_framework.exceptions import ValidationError, PermissionDenied

from accounts.models import Account
from debts import constants
from debts.models import DebtRequest, Debt
from debts.signals import debt_request_done


class DebtRequestService:
    def __init__(
        self,
        creditor_id: int,
        debtor_id: int,
        request_creator: Account,
        **debt_request_data,
    ):
        self.creditor = Account.objects.get(pk=creditor_id)
        self.debtor = Account.objects.get(pk=debtor_id)
        self.creator = request_creator
        self.debt_request_data = debt_request_data

    def create_debt_request(self):
        self._validate_creator()
        self._validate_send_to_itself()
        self._validate_in_friends()

        return DebtRequest.objects.create(
            creditor=self.creditor,
            debtor=self.debtor,
            creator=self.creator,
            **self.debt_request_data,
        )

    def _validate_creator(self):
        if self.creator not in (self.creditor, self.debtor):
            raise ValidationError('Current user should be debtor or creditor.')

    def _validate_in_friends(self):
        if not self.creditor.friends.filter(pk=self.debtor.id).exists():
            raise ValidationError(
                "You're not a friend with your debtor/creditor."
            )

    def _validate_send_to_itself(self):
        if self.creditor == self.debtor:
            raise ValidationError(
                "Cannot send debt to self."
            )


class DebtRequestUpdateService:
    def __init__(
            self,
            debt_request_id: uuid.UUID,
            status: str,
            creator: Account,
    ) -> None:
        self.debt_request = DebtRequest.objects.get(pk=debt_request_id)
        self.status = status
        self.creator = creator

    def update_debt_request(self) -> Optional[Debt]:
        result = self._update_debt_request()
        debt_request_done.send(
            sender=self.debt_request,
            status=self.status,
        )
        return result

    def _update_debt_request(self) -> Optional[Debt]:
        self._validate_creator_is_not_accept_own_debt_request()
        self._validate_creator_is_debt_request_participant()
        self._validate_is_not_active()

        if self.status == constants.STATUS_ACCEPT:
            return self._accept_debt_request()
        elif self.status == constants.STATUS_DECLINE:
            return self._decline_debt_request()
        else:
            raise ValidationError("Status is not correct")

    def _validate_creator_is_not_accept_own_debt_request(self):
        if self.debt_request.creator == self.creator:
            raise ValidationError("Cannot change status of request from creator.")

    def _validate_creator_is_debt_request_participant(self):
        if self.creator not in (self.debt_request.debtor, self.debt_request.creditor):
            raise PermissionDenied

    def _validate_is_not_active(self):
        if not self.debt_request.is_active:
            raise ValidationError("Debt request is not active.")

    def _accept_debt_request(self) -> Debt:
        return Debt.create_from_request(debt_request=self.debt_request)

    def _decline_debt_request(self) -> None:
        self.debt_request.declined = True
        self.debt_request.save()
