from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Customer , Loan
from django.core.serializers import serialize
from .serializers import CustomerSerializer, LoanSerializerAll , LoanSerializer
from .helper import *
from datetime import date , timedelta
from decimal import Decimal
import json



@api_view(['POST'])
def register_customer(request ):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        monthly_salary = data['monthly_salary']

        # Calculate approved limit based on the given formula
        approved_limit = round(36 * monthly_salary / 100000) * 100000

        # Create a new customer
        customer = Customer.objects.create(
            # customer_id=data['customer_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
            phone_number=data.get('phone_number', ''),
        )

        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(pk=loan_id)
    except Loan.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = LoanSerializerAll(loan)
    customer_serialized = CustomerSerializer(loan.customer)
    serializer.data["customer"] = customer_serialized.data
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_loan(request):
    data = request.data
    customer_id  = data['customer_id']
    interest_rate  = data['interest_rate']
    loan_amount  = data['loan_amount']
    tenure  = data['tenure']
    message = "Approved"

    if customer_id:
        customer = Customer.objects.get(pk=customer_id)
        approval , corrected_interest = check_loan_eligibility(customer_id , interest_rate)
    monthly_installment = 0
    if approval == True:
        monthly_installment = calculate_monthly_installment( loan_amount , interest_rate,tenure)
    response_data = {
        "customer_id":customer_id,
        "loan_amount":loan_amount,
        "interest_rate":corrected_interest,
        "approval":approval,
        "message": message,
    }

    if approval :
        response_data["monthly_installment"] = monthly_installment

        new_loan = Loan.objects.create(
            customer = customer,
            loan_amount=loan_amount,
            interest_rate = corrected_interest,
            tenure = tenure,
            monthly_repayment = monthly_installment,
            start_date = date.today(),
            end_date = date.today() + timedelta(days=30 * tenure),
            repayments_left = tenure
        )
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response(response_data,status=status.HTTP_200_OK)
    
    



@api_view(['POST'])
def checkEligibility(request):
    data = request.data
    customer_id  = data['customer_id']
    interest_rate  = data['interest_rate']
    loan_amount  = data['loan_amount']
    tenure  = data['tenure']

    if customer_id:
        customer = Customer.objects.get(pk=customer_id)
        approval ,  corrected_interest = check_loan_eligibility(customer , interest_rate)

        response_data = {
            "customer_id":customer_id,
            "loan_amount":loan_amount,
            "interest_rate":interest_rate,
            "approval":approval,
            "corrected_interest": corrected_interest,
            "tenure":tenure
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
def view_loans_by_customer_id(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id = customer_id)
        loans = Loan.objects.filter(customer = customer)

        # Return response
        result = []

        for loan in loans:
            result.append(LoanSerializer(loan).data)
        return Response(result, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)