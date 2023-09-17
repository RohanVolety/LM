## Loan Management System

The Loan Management System is a Django-based web application that allows users to register, apply for loans, make loan payments, and get statements of their loan transactions. 


## Create a virtual environment  

```sh
$ virtualenv venv
```
```sh
$ source venv/bin/activate
```  

## Install  required dependencies
```sh
$ pip install -r requirements.txt
```
## Setup Models  

```sh
$ python manage.py makemigrations
```
```sh
$ python manage.py migrate 
```
```sh
$ python manage.py runserver
```
  
## Start Celery worker  

```sh
$ celery -A loan_management worker -l info
```



## API END-PONTS  
  
@http://localhost:8000/

1.User Registration (POST API)

Endpoint: `/api/register-user/`

Method: POST

Description: Registers a new user

Request Body (JSON):
```
{
  "Aadhar ID": "unique_user_id",
  "name": "John Doe",
  "email_id": "rohan@gmail.com",
  "annual_income": 1500000,
  "credit_score":500

}
```
Response Json(Success):
```
{
  "Error": null,
  "unique_user_id": "6"
}

```
Response Json(Faliure):

```
{
  "Error": "Invalid data provided. Please check your input fields."
}

```

2. Loan Application (POST API)

Endpoint: `/api/apply-loan/`

Method: POST

Description: Allows user to apply for a loan based on specific criteria.

Request Body (JSON):

```
{
  "unique_user_id": "user_id",
  "loan_type": "Car",
  "loan_amount": 800000,
  "interest_rate": 20,
  "term_period": 24,
  "disbursement_date": "2023-10-01"
}

```

Response Json (Success):
```
{
  "Error": null,
  "Loan_id": 1,
  "Due_dates": [
    {
      "Date": "2023-10-01",
      "Amount_due": 15000.00
    },
  ]
}

```
Response Json (Faliure):

```
{
  "Error": "User's credit score is below 450."
}
```
3. Register Payment (POST API)

Endpoint: `/api/make-payment/`

Method: POST

Description: Allows a user to make a payment towards an EMI.

Request Body (JSON):

```
{
  "Loan_id": "loan_id",
  "Amount": 15000.00
}

```
Response Json (Success):

```
{
  "Error": null
}


```
Response JSON (Failure):

```
{
  "Error": "Payment for the same date already exists."
}


```


4. Get Statement and Future Dues (GET API)

Endpoint: `/api/get-statement/`

Method: GET

Description: Retrieves the statement of loan transactions and upcoming EMIs.

Query Parameter: Loan_id (Loan identifier)

Response JSON (Success):

```
{
  "Error": null,
  "Past_transactions": [
    {
      "Date": "2023-10-01",
      "Principal": 12000.00,
      "Interest": 3000.00,
      "Amount_paid": 15000.00
    },
],
  "Upcoming_transactions": [
    {
      "Date": "2023-11-01",
      "Amount_due": 15000.00
    },
  ]
}


```
Response JSON (Failure):

```
{
  "Error": "Loan not found."
}

```


Model Schema

### 1. **User**

* aadhar_id (CharField): A unique identifier for each user.

* name (CharField): The name of the user.

* email (EmailField): The email address of the user.

* annual_income (DecimalField): The annual income of the user.

* credit_score (IntegerField): The credit score of the user (default value: 450).

### 2. **Loan**

* user (ForeignKey to User): A foreign key relationship with the User model.

* loan_type (CharField): The type of the loan like 'Car,' 'Home,' 'Education,' or 'Personal.'

* loan_amount (DecimalField): The loan amount.

* interest_rate (DecimalField): The interest rate.

* term_period (PositiveIntegerField): The term period of the loan.

* disbursement_date (DateField): The date when the loan was disbursed.


### 3. **Transaction**

* user (ForeignKey to User): A foreign key relationship with the User model.

* date (DateField): The date of the transaction.

* amount (DecimalField): The transaction amount .

* transaction_type (CharField): The type of the transaction, either 'DEBIT' or 'CREDIT.'


