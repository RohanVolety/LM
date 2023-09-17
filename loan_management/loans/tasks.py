from celery import shared_task
from .models import User, Transaction
import math
from datetime import timedelta


@shared_task
def calculate_credit_score(user_id):    
    user = User.objects.get(id=user_id)

    # Calculate the total account balance for the user
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


@shared_task
def calculate_emis(loan_amount, interest_rate, term_period, disbursement_date, monthly_income):
    # Calculate the monthly interest rate
    monthly_interest_rate = (interest_rate / 12) / 100

    # Calculate the EMI amount
    emi_numerator = loan_amount * monthly_interest_rate
    emi_denominator = 1 - math.pow(1 + monthly_interest_rate, -term_period)
    emi_amount = emi_numerator / emi_denominator

    # Initialize variables
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
