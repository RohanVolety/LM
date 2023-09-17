"""
URL configuration for loan_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from loans.views import apply_loan
from loans.views import get_statement
from loans.views import register_user
from loans.views import make_payment



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register-user/', register_user, name='register_user'),
    path('api/apply-loan/', apply_loan, name='apply_loan'),
     path('api/make-payment/', make_payment, name='make_payment'),
     path('api/get-statement/', get_statement, name='get_statement'),
]
