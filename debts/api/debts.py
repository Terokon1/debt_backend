from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from debts import selectors
from debts.models import Debt
from debts.serializers import OutputDebtSerializer


class DebtAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List of debts",
        tags=["debts"],
        responses={
            200: OutputDebtSerializer(many=True),
        }
    )
    def get(self, request):
        user: Account = request.user
        debts = selectors.get_related_debts(user)

        result = OutputDebtSerializer(debts, many=True).data
        return Response(data=result)


class DetailDebtApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Detail debt",
        tags=["debts"],
        responses={
            200: OutputDebtSerializer(),
        }
    )
    def get(self, request, pk):
        debt = get_object_or_404(Debt, pk=pk)

        result = OutputDebtSerializer(debt).data
        return Response(data=result)
