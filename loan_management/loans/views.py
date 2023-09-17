# loans/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User, Loan, Transaction
from .serializers import LoanSerializer, UserSerializer
import math
from datetime import date, timedelta
from .tasks import calculate_credit_score

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)    
    if serializer.is_valid():
        # Save the user data
        user = serializer.save()        
        #calculate_credit_score.delay(user.id)
        calculate_credit_score(user.id)

        response_data = {
            "Error": None,
            "unique_user_id": str(user.id)  # Convert the UUID to a string
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "Error": "Invalid data provided. Please check your input fields."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def apply_loan(request):
    # Extract user_id from the request data
    user_id = request.data.get('unique_user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        response_data = {
            "Error": "User not found."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    # Check if the user meets the credit score and income requirements
    if user.credit_score < 450:
        response_data = {
            "Error": "User's credit score is below 450."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    if user.annual_income < 150000:
        response_data = {
            "Error": "User's annual income is below Rs. 1,50,000."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    # Extract loan data from the request
    serializer = LoanSerializer(data=request.data)
    if serializer.is_valid():
        loan_type = serializer.validated_data['loan_type']

        # Check loan amount bounds based on the loan type
        loan_amount = serializer.validated_data['loan_amount']
        if (loan_type == 'Car' and loan_amount > 750000) or \
           (loan_type == 'Home' and loan_amount > 8500000) or \
           (loan_type == 'Educational' and loan_amount > 5000000) or \
           (loan_type == 'Personal' and loan_amount > 1000000):
            response_data = {
                "Error": f"Loan amount exceeds the allowed limit for {loan_type} loan."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)        
        loan = Loan.objects.create(
            user=user,
            loan_type=loan_type,
            loan_amount=loan_amount,
            interest_rate=serializer.validated_data['interest_rate'],
            term_period=serializer.validated_data['term_period'],
            disbursement_date=serializer.validated_data['disbursement_date']
        )

        response_data = {
            "Error": None,
            "Loan_id": loan.id
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "Error": "Invalid loan data provided. Please check your input fields."
        }
    
    # Calculate EMIs
    emi_dates = calculate_emis(loan_amount, interest_rate, term_period, disbursement_date, user.annual_income)

    if emi_dates is None:
        response_data = {
            "Error": "EMI calculation failed. Check loan amount, interest rate, or monthly income."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Update the loan object with EMI details
    loan.emi_details = emi_dates
    loan.save()

    response_data = {
        "Error": None,
        "Loan_id": loan.id,
        "Due_dates": emi_dates
    }
    return Response(response_data, status=status.HTTP_200_OK)
    




def calculate_emis(loan_amount, interest_rate, term_period, disbursement_date, monthly_income):
    # Calculate the monthly interest rate
    monthly_interest_rate = (interest_rate / 12) / 100

    # Calculate the EMI amount
    emi_numerator = loan_amount * monthly_interest_rate
    emi_denominator = 1 - math.pow(1 + monthly_interest_rate, -term_period)
    emi_amount = emi_numerator / emi_denominator
    
    emi_dates = []
    remaining_principal = loan_amount
    total_interest = 0

    
    for month in range(term_period):
        
        monthly_interest = remaining_principal * monthly_interest_rate

        # Calculate principal for the month
        principal_payment = emi_amount - monthly_interest

        
        if emi_amount > (0.6 * monthly_income):
            return None  

        
        total_interest += monthly_interest

        
        due_date = disbursement_date + timedelta(days=30)

        # Add EMI details to the list
        emi_dates.append({
            "Date": due_date,
            "Amount_due": emi_amount
        })

        
        remaining_principal -= principal_payment

    
    if total_interest <= 10000:
        return None  # Total interest is not sufficient

    return emi_dates




@api_view(['POST'])
def make_payment(request):    
    loan_id = request.data.get('Loan_id')
    payment_amount = request.data.get('Amount')

    try:
        loan = Loan.objects.get(id=loan_id)
    except Loan.DoesNotExist:
        response_data = {
            "Error": "Loan not found."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    
    for emi in loan.emi_details:
        if emi['Date'] == payment_date:
            response_data = {
                "Error": "Payment for the same date already exists."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Check if previous EMIs are due
    current_date = date.today()
    for emi in loan.emi_details:
        if emi['Date'] < current_date:
            response_data = {
                "Error": "Previous EMIs are due."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    
    next_emi = None
    for emi in loan.emi_details:
        if emi['Date'] > current_date:
            next_emi = emi
            break

    if next_emi is None:
        response_data = {
            "Error": "No more EMIs are due."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    
    if payment_amount != next_emi['Amount_due']:
        next_emi['Amount_due'] = payment_amount    
    loan.save()
    response_data = {
        "Error": None
    }
    return Response(response_data, status=status.HTTP_200_OK)





@api_view(['GET'])
def get_statement(request):    
    loan_id = request.query_params.get('Loan_id')
    try:
        loan = Loan.objects.get(id=loan_id)
    except Loan.DoesNotExist:
        response_data = {
            "Error": "Loan not found."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)    
    if loan.is_closed:
        response_data = {
            "Error": "Loan is closed."
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    current_date = date.today()
    past_transactions = []
    upcoming_transactions = []

    
    for emi in loan.emi_details:
        if emi['Date'] < current_date:
            # Payment for past month
            principal_due = None  
            interest_on_principal = None  
            amount_paid = emi['Amount_due']
            past_transactions.append({
                "Date": emi['Date'],
                "Principal": principal_due,
                "Interest": interest_on_principal,
                "Amount_paid": amount_paid
            })
        else:
            
            upcoming_transactions.append({
                "Date": emi['Date'],
                "Amount_due": emi['Amount_due']
            })

    response_data = {
        "Error": None,
        "Past_transactions": past_transactions,
        "Upcoming_transactions": upcoming_transactions
    }
    return Response(response_data, status=status.HTTP_200_OK)



def calculate_credit_score(user_id):    
    user = User.objects.get(id=user_id)

    
    transactions = Transaction.objects.filter(user=user)
    total_balance = sum(tr.amount if tr.transaction_type == 'CREDIT' else -tr.amount for tr in transactions)

    
    if total_balance >= 1000000:
        user.credit_score = 900
    elif total_balance <= 100000:
        user.credit_score = 300
    else:
        balance_diff = total_balance - 100000
        credit_score_change = balance_diff // 15000 * 10
        user.credit_score = 300 + credit_score_change

    user.save()
