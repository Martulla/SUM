import datetime

from django import forms

from sumapp.models import CATEGORY


class LoginForm(forms.Form):
    login = forms.CharField(max_length=120)
    password = forms.CharField(widget=forms.PasswordInput)

class QueryForm(forms.Form):
    dream = forms.CharField(label="Marzenie", max_length=120, help_text='wpisz na co chcesz zaoszczędzić')
    price_of_dream = forms.IntegerField(label="Jaki jest koszt Twojego marzenia", help_text='wpisz kwotę')
    income_monthly = forms.IntegerField(label="Miesięczny dochód", help_text='wpisz średni lub ostatni miesięczny dochód "na rękę"')
    income_monthly_date = forms.DateField(label="Data dochodu", widget = forms.SelectDateWidget, help_text='wpisz datę ostatniego dochodu')
    expense_monthly = forms.IntegerField(label="Miesięczne stałe wydatki", help_text='wpisz całościową kwotę stałych opłat')
    unregular_expense_price = forms.IntegerField(label="Średnie wydatki miesięczne poza regularnymi opłatami", help_text='wpisz średnią kwotę innych wydatków np. jedzenie, przyjemności, podróże. Zsumowaną')


class CalculationForm(forms.Form):
        submit = forms.HiddenInput()


class DailyCalculationForm(forms.Form):
    daily_expanse = forms.DecimalField(label='Wydatek', required=False)
    for_what = forms.CharField(label='Na co?', required=False)
    category = forms.ChoiceField(label="Kategoria", choices=CATEGORY, required=False)
    date_expanse = forms.DateField(label= 'Kiedy?', initial=datetime.date.today)
    unxpected_income = forms.DecimalField(label='Niepospodziewany dochód', required=False)
    from_who = forms.CharField(label='Źródło dochodu', required=False)
    date_income = forms.DateField(label= 'Kiedy?', initial=datetime.date.today)



class MailForm(forms.Form):
    mail_adress = forms.EmailField(label= 'wpisz swój adres mailowy')


class ResumeForm(forms.Form):
    submit = forms.HiddenInput()


class ReturnForm(forms.Form):
    submit = forms.HiddenInput()







