from rest_framework import serializers

from accounts.serializers import OutputAccountShortSerializer
from debts.models import Debt


class OutputDebtSerializer(serializers.ModelSerializer):
    debtor = OutputAccountShortSerializer()
    creditor = OutputAccountShortSerializer()

    class Meta:
        model = Debt
        fields = [
            'id', 'money', 'creditor',
            'debtor', 'description', 'created',
        ]
