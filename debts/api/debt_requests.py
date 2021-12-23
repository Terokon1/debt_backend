from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from debts import selectors
from debts.models import DebtRequest
from debts.serializers import (
    OutputDebtSerializer,
    InputDebtRequestSerializer,
    OutputDebtRequestSerializer,
    InputDebtRequestUpdateSerializer,
)
from debts.services import DebtRequestService, DebtRequestUpdateService


class DebtRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List of debt requests",
        tags=["debt requests"],
        responses={
            200: OutputDebtRequestSerializer(many=True),
        },
    )
    def get(self, request):
        debt_requests = selectors.get_related_debt_requests(request.user)

        output_serializer = OutputDebtRequestSerializer(
            debt_requests,
            many=True,
            context={'request': request},
        )
        return Response(
            data=output_serializer.data,
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Create debt request",
        tags=["debt requests"],
        request_body=InputDebtRequestSerializer(),
        responses={
            201: 'Empty',
            400: """
One of errors: 
   - Current user should be debtor or creditor.
   - You're not a friend with your debtor/creditor.
   - Cannot send debt to self.
"""
        })
    def post(self, request):
        serializer = InputDebtRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        debtor_id = data.pop('debtor_id')
        creditor_id = data.pop('creditor_id')

        DebtRequestService(
            creditor_id=creditor_id,
            debtor_id=debtor_id,
            request_creator=self.request.user,
            **data,
        ).create_debt_request()

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Accept/decline debt request",
        request_body=InputDebtRequestUpdateSerializer(),
        tags=["debt requests"],
        responses={
            200: OutputDebtSerializer(),
            204: 'Empty, if request is deleted.',
            400: """
One of Errors:  
- Cannot change status of request from creator.  
- Debt request is not active.
"""
        },
    )
    def patch(self, request):
        serializer = InputDebtRequestUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            debt_request = DebtRequestUpdateService(
                **serializer.validated_data,
                creator=self.request.user,
            ).update_debt_request()
        except DebtRequest.DoesNotExist:
            raise NotFound

        if debt_request:
            data = OutputDebtSerializer(debt_request).data
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
