from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from debts import constants
from debts.models import DebtRequest
from debts.serializers import OutputDebtRequestSerializer, OutputDebtSerializer
import redis_utils


debt_request_done = Signal()


@receiver(post_save, sender=DebtRequest)
def notify_request_created(sender, instance: DebtRequest, created: bool, **kwargs):
    if not created:
        return

    if instance.creator == instance.debtor:
        to_user = instance.creditor
    else:
        to_user = instance.debtor

    data = {
        'event': 'created',
        'type': 'DebtRequest',
        'object': OutputDebtRequestSerializer(
            instance,
            context={'user': to_user},
        ).data,
    }
    event_created = redis_utils.Event(to_user.pk, data)
    redis_utils.send_to_pub([event_created])


@receiver(debt_request_done)
def notify_debt_request_creator(sender: DebtRequest, status: str, **kwargs):
    if status not in (constants.STATUS_ACCEPT, constants.STATUS_DECLINE):
        raise Exception("Status is incorrect!")

    creator = sender.creator

    data = {
        'event': 'status_updated',
        'type': 'DebtRequest',
        'object': OutputDebtRequestSerializer(
            sender,
            context={'user': creator},
        ).data,
        'status': status,
    }
    if status == constants.STATUS_ACCEPT:
        debt = sender.connected_debt
        debt_data = {
            'type': 'Debt',
            'object': OutputDebtSerializer(debt).data,
        }

        data['debt'] = debt_data

    event_debt_request_updated = redis_utils.Event(str(creator.id), data)
    redis_utils.send_to_pub([event_debt_request_updated])
