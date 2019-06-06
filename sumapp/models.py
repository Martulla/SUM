import datetime

from django.contrib import admin
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models

# Create your models here.



class MonthlyIncome(models.Model):
    income = models.DecimalField(max_digits = 8, decimal_places=2, null=False)
    income_date = models.DateField(default=datetime.datetime.now().date(), null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return 'MonthlyIncomme: {} '.format(self.income)


class UnregularExpense(models.Model):
    expense = models.DecimalField(max_digits=6, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return 'UnregularExpense: {} '.format(self.expense)



class MonthlyExpense(models.Model):
    expense = models.DecimalField(max_digits = 8, decimal_places=2, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,  default=None)

    def __str__(self):
        return 'MonthlyExpense: {} '.format(self.expense)


class Dream(models.Model):
    dream = models.CharField(max_length=120, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.dream


class IncomeExpense(models.Model):
    additional_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_expense =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_date = models.DateTimeField(default=datetime.datetime.now)
    expense_date = models.DateTimeField(default=datetime.datetime.now)
    source_income = models.CharField(max_length= 30)
    expense_object = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)


class SteadyData(models.Model):
    enter_savings = models.DecimalField(max_digits=20,decimal_places= 2, default=0)
    new_savings = models.DecimalField(max_digits=20,decimal_places= 2, default=0)
    enter_all_unregular_expese_you_may_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    new_all_unregular_expese_you_may_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    login_check = models.IntegerField()
    monthly_savings = models.DecimalField(max_digits=20,decimal_places= 2, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
