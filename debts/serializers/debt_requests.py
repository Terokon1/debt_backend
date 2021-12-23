from rest_framework import serializers

from accounts.serializers import OutputAccountShortSerializer
from debts import constants
from debts.models import DebtRequest


class InputDebtRequestSerializer(serializers.Serializer):
    money = serializers.DecimalField(max_digits=12, decimal_places=2)
    creditor_id = serializers.UUIDField()
    debtor_id = serializers.UUIDField()
    description = serializers.CharField(allow_blank=True)


class OutputDebtRequestSerializer(serializers.ModelSerializer):
    debtor = OutputAccountShortSerializer()
    creditor = OutputAccountShortSerializer()
    is_yours = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()

    def get_is_yours(self, obj) -> bool:
        if self.context.get('request'):
            user = self.context['request'].user
        else:
            user = self.context['user']
        return user == obj.creator

    class Meta:
        model = DebtRequest
        fields = [
            'id', 'money', 'creditor',
            'debtor', 'is_yours', 'description',
            'created', 'is_active',
        ]


class InputDebtRequestUpdateSerializer(serializers.Serializer):
    debt_request_id = serializers.UUIDField()
    status = serializers.ChoiceField(constants.DEBT_REQUEST_STATUS)
