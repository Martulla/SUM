import datetime
import math

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags


from .utils import render_to_pdf

from django.views import View

from sumapp.forms import QueryForm, DailyCalculationForm, MailForm, CalculationForm, ResumeForm, ReturnForm
from sumapp.models import Dream, MonthlyIncome, MonthlyExpense, UnregularExpense, IncomeExpense, SteadyData, Category, \
    LastLogin


class StartPageView(View):
    def get(self, request):
        return render(request, 'sumapp/startpage.html')

class LoginNewView(View):
    def get(self, request):
        form = AuthenticationForm()
        ctx = {'form':form}
        return render(request, 'sumapp/user.html', ctx)

    def post(self, request):
        form = AuthenticationForm(data= request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                new_last_login = LastLogin.objects.get(user_id = user.id)
                new_last_login.last_login = datetime.datetime.now()
                new_last_login.save()
                login_check_get = SteadyData.objects.get(user_id=user.id)
                date = MonthlyIncome.objects.get(user_id=user.id)
                last_income_date = date.income_date
                days = datetime.date.today() - last_income_date

                if days >=  datetime.timedelta(days = 30):
                    url = reverse('sum/sumapp:resume', kwargs={'id': user.id})
                    return redirect(url)
                elif login_check_get.login_check == 1:
                    url = reverse('sum/sumapp:daily-calculation', kwargs={'id': user.id})
                    print(days)
                    return redirect(url)
                else:
                    return redirect('sum/sumapp:calculation', id = user.id)

        ctx = {'form':form}
        return render(request, 'sumapp/user.html', ctx)


class AddUserView(View):
    def get(self, request):
        form = UserCreationForm()
        ctx = {'form':form}
        return render(request, 'sumapp/registration.html', ctx)
    def post(self, request):
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user_name = form.cleaned_data['username']
            form.save()
            new_user = User.objects.get(username =user_name )
            if new_user:
                login(request, new_user)
                new_last_login = LastLogin(last_login=datetime.datetime.now(),
                                           user=new_user)
                new_last_login.save()

            return redirect('sum/sumapp:query', user_id = new_user.id)
        ctx = {'form': form}
        return render(request, 'sumapp/registration.html', ctx)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('sum/sumapp:index')


class QueryView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        form = QueryForm()
        return render(request, "sumapp/query.html", {'form':form})

    def post(self, request, user_id):
        form = QueryForm(request.POST)
        if form.is_valid():
            dream_from_form = form.cleaned_data['dream']
            price_of_dream_from_form = form.cleaned_data['price_of_dream']
            income_monthly_form_form = form.cleaned_data['income_monthly']
            income_monthly_date_form_form = form.cleaned_data['income_monthly_date']
            expense_monthly_form_form = form.cleaned_data['expense_monthly']
            unregular_expense_price_form_form = form.cleaned_data['unregular_expense_price']
            expense_all = expense_monthly_form_form + unregular_expense_price_form_form

            if income_monthly_form_form < expense_all:
                ctx = {'form': QueryForm()}
                messages.info(request,'Podałeś za niski dochód, żeby mieć takie wydatki')
                render(request, "sumapp/query.html", ctx)
            elif income_monthly_form_form == expense_all:
                ctx = {'form': QueryForm()}
                messages.info(request, 'Masz dochód równy wydatkom. Nic nie uda Ci się zaoszczędzić')
                render(request, "sumapp/query.html", ctx)
            else:
                user = User.objects.get(pk = user_id)

                try:
                    dream_check = Dream.objects.get(user_id = user.id)
                    if dream_check:
                        dream_check.dream = dream_from_form
                        dream_check.price = price_of_dream_from_form
                        dream_check.save()
                except Dream.DoesNotExist:
                    new_dream = Dream(dream=dream_from_form,
                                      price=price_of_dream_from_form,
                                      user=user)
                    new_dream.save()

                try:
                    monthly_income_check = MonthlyIncome.objects.get(user_id = user.id)
                    if monthly_income_check:
                        monthly_income_check.income = income_monthly_form_form
                        monthly_income_check.income_date = income_monthly_date_form_form
                        monthly_income_check.save()
                except MonthlyIncome.DoesNotExist:
                    new_monthly_income = MonthlyIncome(income = income_monthly_form_form,
                                                       income_date = income_monthly_date_form_form,
                                                       user = user)
                    new_monthly_income.save()

                try:
                    monthly_expanse_check = MonthlyExpense.objects.get(user_id = user.id)
                    if monthly_expanse_check:
                        monthly_expanse_check.expense = expense_monthly_form_form
                        monthly_expanse_check.save()
                except MonthlyExpense.DoesNotExist:
                    new_monthly_expanse = MonthlyExpense(expense=expense_monthly_form_form,
                                                            user=user)
                    new_monthly_expanse.save()

                try:
                    unregular_expense_check = UnregularExpense.objects.get(user_id = user.id)
                    if unregular_expense_check:
                        unregular_expense_check.expense = unregular_expense_price_form_form
                        unregular_expense_check.save()
                except UnregularExpense.DoesNotExist:
                    new_unregular_expense =  UnregularExpense(expense = unregular_expense_price_form_form,
                                                              user = user)
                    new_unregular_expense.save()

                mon_ex = MonthlyExpense.objects.get(user_id = user.id)
                mon_in = MonthlyIncome.objects.get(user_id = user.id)
                mon_un_ex = UnregularExpense.objects.get(user_id = user.id)

                savings = mon_in.income - mon_ex.expense - mon_un_ex.expense

                try:
                    steady_data_check = SteadyData.objects.get(user_id = user.id)
                    if steady_data_check:
                        steady_data_check.enter_savings = savings + steady_data_check.monthly_savings
                        steady_data_check.new_savings = savings + steady_data_check.monthly_savings
                        steady_data_check.enter_all_unregular_expese_you_may_spend = mon_un_ex.expense
                        steady_data_check.new_all_unregular_expese_you_may_spend = mon_un_ex.expense
                        steady_data_check.login_check = 0
                        steady_data_check.save()
                except SteadyData.DoesNotExist:
                    new_steady_data = SteadyData(enter_savings = savings,
                                                 new_savings = savings,
                                                 enter_all_unregular_expese_you_may_spend= mon_un_ex.expense,
                                                 new_all_unregular_expese_you_may_spend = mon_un_ex.expense,
                                                 login_check = 0,
                                                 monthly_savings = 0,
                                                 user = user)
                    new_steady_data.save()

                return redirect('sum/sumapp:calculation', id = user.id)
        return render(request, "sumapp/query.html", {'form': form})


class QueryUpdateView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        monthly_steady_income = MonthlyIncome.objects.get(user_id=user.id)
        monthly_steady_expense = MonthlyExpense.objects.get(user_id=user.id)
        unregular_mothly_expense = UnregularExpense.objects.get(user_id=user.id)
        dream = Dream.objects.get(user_id=user.id)
        form = QueryForm(initial={'dream': dream.dream,
                                    'price_of_dream': dream.price,
                                                  'income_monthly': monthly_steady_income.income,
                                                  'income_monthly_date': monthly_steady_income.income_date,
                                                  'exense_monthly': monthly_steady_expense.expense,
                                                  'unregular_expense_price': unregular_mothly_expense.expense})
        return render(request, "sumapp/query.html", {'form': form})

    def post(self, request, user_id):
        form = QueryForm(request.POST)
        if form.is_valid():
            dream_from_form = form.cleaned_data['dream']
            price_of_dream_from_form = form.cleaned_data['price_of_dream']
            income_monthly_form_form = form.cleaned_data['income_monthly']
            income_monthly_date_form_form = form.cleaned_data['income_monthly_date']
            expense_monthly_form_form = form.cleaned_data['expense_monthly']
            unregular_expense_price_form_form = form.cleaned_data['unregular_expense_price']
            expense_all = expense_monthly_form_form + unregular_expense_price_form_form

            if income_monthly_form_form < expense_all:
                ctx = {'form': QueryForm()}
                messages.info(request, 'Podałeś za niski dochód, żeby mieć takie wydatki')
                render(request, "sumapp/query.html", ctx)
            elif income_monthly_form_form == expense_all:
                ctx = {'form': QueryForm()}
                messages.info(request, 'Masz dochód równy wydatkom. Nic nie uda Ci się zaoszczędzić')
                render(request, "sumapp/query.html", ctx)
            else:
                user = User.objects.get(pk=user_id)
                try:
                    dream_check = Dream.objects.get(user_id=user.id)
                    if dream_check:
                        dream_check.dream = dream_from_form
                        dream_check.price = price_of_dream_from_form
                        dream_check.save()
                except Dream.DoesNotExist:
                    new_dream = Dream(dream=dream_from_form,
                                      price=price_of_dream_from_form,
                                    user=user)
                    new_dream.save()

                try:
                    monthly_income_check = MonthlyIncome.objects.get(user_id=user.id)
                    if monthly_income_check:
                        monthly_income_check.income = income_monthly_form_form
                        monthly_income_check.income_date = income_monthly_date_form_form
                        monthly_income_check.save()
                except MonthlyIncome.DoesNotExist:
                    new_monthly_income = MonthlyIncome(income=income_monthly_form_form,
                                                       income_date=income_monthly_date_form_form,
                                                       user=user)
                    new_monthly_income.save()

                try:
                    monthly_expanse_check = MonthlyExpense.objects.get(user_id=user.id)
                    if monthly_expanse_check:
                        monthly_expanse_check.expense = expense_monthly_form_form
                        monthly_expanse_check.save()
                except MonthlyExpense.DoesNotExist:
                    new_monthly_expanse = MonthlyExpense(expense=expense_monthly_form_form,
                                                         user=user)
                    new_monthly_expanse.save()

                try:
                    unregular_expense_check = UnregularExpense.objects.get(user_id=user.id)
                    if unregular_expense_check:
                        unregular_expense_check.expense = unregular_expense_price_form_form
                        unregular_expense_check.save()
                except UnregularExpense.DoesNotExist:
                    new_unregular_expense = UnregularExpense(expense=unregular_expense_price_form_form,
                                                             user=user)
                    new_unregular_expense.save()

                mon_ex = MonthlyExpense.objects.get(user_id=user.id)
                mon_in = MonthlyIncome.objects.get(user_id=user.id)
                mon_un_ex = UnregularExpense.objects.get(user_id=user.id)

                savings = mon_in.income - mon_ex.expense - mon_un_ex.expense

                try:
                    steady_data_check = SteadyData.objects.get(user_id=user.id)
                    if steady_data_check:
                        steady_data_check.enter_savings = savings + steady_data_check.monthly_savings
                        steady_data_check.new_savings = savings + steady_data_check.monthly_savings
                        steady_data_check.enter_all_unregular_expese_you_may_spend = mon_un_ex.expense
                        steady_data_check.new_all_unregular_expese_you_may_spend = mon_un_ex.expense
                        steady_data_check.login_check = 0
                        steady_data_check.save()
                except SteadyData.DoesNotExist:
                    new_steady_data = SteadyData(enter_savings=savings,
                                                 new_savings=savings,
                                                 enter_all_unregular_expese_you_may_spend=mon_un_ex.expense,
                                                 new_all_unregular_expese_you_may_spend=mon_un_ex.expense,
                                                 login_check=0,
                                                 monthly_savings=0,
                                                 user=user)
                    new_steady_data.save()

                return redirect('sum/sumapp:calculation', id=user.id)
        return render(request, "sumapp/query.html", {'form': form})


class CalculationView(LoginRequiredMixin, View):
    def get(self, request, id):
        monthly_steady_income = MonthlyIncome.objects.get(user_id = request.user.id)
        mon_steady_in = monthly_steady_income.income
        monthly_steady_expense = MonthlyExpense.objects.get(user_id = request.user.id)
        mon_steady_ex = monthly_steady_expense.expense
        unregular_mothly_expense = UnregularExpense.objects.get(user_id = request.user.id)
        un_monthly_ex = unregular_mothly_expense.expense
        dream = Dream.objects.get(user_id = id)
        dream_price = dream.price
        all_monthly_expense = mon_steady_ex +un_monthly_ex
        savings = SteadyData.objects.get(user_id = id)

        if dream_price <= savings.enter_savings:
            realization_time = 1
        else:
            number_of_month = dream_price/savings.enter_savings
            realization_time = math.ceil(number_of_month) #zaokrągla w górę ilość miesięcy
        form = CalculationForm()
        ctx = {'income' : mon_steady_in,
                'expense' : all_monthly_expense,
                'dream':dream,
                'price': dream_price,
                'realization': realization_time,
               'form': form}
        messages.info(request, 'Zastanów się czy na pewno poprawie wpisałeś/łaś dane. Po rozpoczęciu oszczędzania edycja będzie możliwa za 30 dni od daty miesięcznego dochodu.')
        return render(request, "sumapp/calculation.html",ctx)

    def post(self, request, id):
        form = CalculationForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id = id)
            login_check = SteadyData.objects.get(user_id=user.id)
            if login_check.login_check == 1:
                login_check.login_check = 1
                login_check.save()
            else:
                login_check.login_check = 1
                login_check.save()
            return redirect('sum/sumapp:daily-calculation', id = user.id)
        return render(request, "sumapp/calculation.html",{'form':form} )


class DailyCalculation(LoginRequiredMixin, View):
    def get(self, request, id):
        dream = Dream.objects.get(user_id=id)
        dream_price = dream.price
        savings = SteadyData.objects.get(user_id = id)
        all_unregular_expese_you_may_spend_get = SteadyData.objects.get(user_id = id)
        all_unregular_expese_you_may_spend = all_unregular_expese_you_may_spend_get.new_all_unregular_expese_you_may_spend

        if all_unregular_expese_you_may_spend > 0:
            ctx = {'form': DailyCalculationForm(),
                   'unregular_expanse': all_unregular_expese_you_may_spend,
                   'dream': dream,
                   'price': dream_price,
                   'savings': savings.new_savings
                   }

        if all_unregular_expese_you_may_spend <= 0 and (-1 * all_unregular_expese_you_may_spend) <= savings.enter_savings:
            ctx = {'form': DailyCalculationForm(),
                   'unregular_expanse': 0,
                   'dream': dream,
                   'price': dream_price,
                   'savings': savings.new_savings
                   }
            messages.info(request, 'Przejadasz oszczędności !')

        if (-1 * all_unregular_expese_you_may_spend) > savings.enter_savings:
            ctx = {'form': DailyCalculationForm(),
                   'unregular_expanse': 0,
                   'dream': dream,
                   'price': dream_price,
                   'savings': savings.new_savings
                   }
            messages.info(request, 'Oszczędności zostały przejedzone. Teraz żyjesz na kredyt')


        income_expense = IncomeExpense.objects.last()
        if income_expense:
            if all_unregular_expese_you_may_spend > 0:
                count_savings = income_expense.additional_expense + savings.enter_savings
                if count_savings >= savings.enter_savings:
                    savings.new_savings = savings.enter_savings
                else:
                    savings.new_savings = savings.enter_savings - income_expense.additional_expense + income_expense.additional_income
                    ctx = {'form': DailyCalculationForm(),
                       'unregular_expanse': 0,
                       'dream': dream,
                       'price': dream_price,
                       'savings': savings.new_savings
                                }
        else:
            ctx = {'form': DailyCalculationForm(),
                   'unregular_expanse': all_unregular_expese_you_may_spend,
                   'dream': dream,
                   'price': dream_price,
                   'savings': savings.new_savings
                   }


        return render(request, 'sumapp/daily-calculation.html', ctx)

    def post(self, request,id):
        form = DailyCalculationForm(request.POST)
        if form.is_valid():
            daily_expanse_from_form = form.cleaned_data['daily_expanse']
            for_what_from_form = form.cleaned_data['for_what']
            date_income_from_form = form.cleaned_data['date_income']
            unxpected_income_form_form = form.cleaned_data['unxpected_income']
            from_who_monthly_form_form = form.cleaned_data['from_who']
            date_expanse_form_form = form.cleaned_data['date_expanse']
            category_from_form = form.cleaned_data['category']
            new_category = Category(name = category_from_form,
                                    user = request.user)
            new_category.save()
            new_category_for_now_record = Category.objects.last()

            if daily_expanse_from_form and unxpected_income_form_form:
                new_record = IncomeExpense(additional_income=unxpected_income_form_form,
                                           additional_expense=daily_expanse_from_form,
                                           income_date=date_income_from_form,
                                           expense_date=date_expanse_form_form,
                                           source_income=from_who_monthly_form_form,
                                           expense_object=for_what_from_form,
                                           user=request.user,
                                           category = new_category_for_now_record
                                            )
                new_record.save()
            elif daily_expanse_from_form and unxpected_income_form_form == None:
                unxpected_income_form_form = 0
                new_record = IncomeExpense(additional_income=unxpected_income_form_form,
                                           additional_expense=daily_expanse_from_form,
                                           income_date=date_income_from_form,
                                           expense_date=date_expanse_form_form,
                                           source_income=from_who_monthly_form_form,
                                           expense_object=for_what_from_form,
                                           user=request.user,
                                           category=new_category_for_now_record
                                           )
                new_record.save()

            else:
                daily_expanse_from_form = 0
                new_record = IncomeExpense(additional_income=unxpected_income_form_form,
                                           additional_expense=daily_expanse_from_form,
                                           income_date=date_income_from_form,
                                           expense_date=date_expanse_form_form,
                                           source_income=from_who_monthly_form_form,
                                           expense_object=for_what_from_form,
                                           user=request.user,
                                           category=new_category_for_now_record
                                           )
                new_record.save()



            unregular_monthly_expense = UnregularExpense.objects.get(user_id=id)
            un_monthly_ex = unregular_monthly_expense.expense
            additional_income_expense = IncomeExpense.objects.filter(user_id=id)
            additional_exepense_result = 0
            for additional_exepense in additional_income_expense:
                if additional_exepense.additional_expense:
                    additional_exepense_result += additional_exepense.additional_expense
                all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result


            additional_income_expense = IncomeExpense.objects.filter(user_id=id)
            addittional_income_result = 0
            for addittional_income in additional_income_expense:
                if addittional_income.additional_income:
                    addittional_income_result += addittional_income.additional_income
                all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result + addittional_income_result

            savings = SteadyData.objects.get(user_id=id)

            if all_unregular_expese_you_may_spend <=0 and (-1 * all_unregular_expese_you_may_spend) <= savings.enter_savings:
                count_expense = (-1 * all_unregular_expese_you_may_spend)
                savings.new_savings = savings.enter_savings - count_expense


            if (-1 *all_unregular_expese_you_may_spend) > savings.enter_savings:
                conut_expense = (-1 * all_unregular_expese_you_may_spend)
                savings.new_savings = savings.enter_savings - conut_expense


            if all_unregular_expese_you_may_spend > 0:
                count_savings = daily_expanse_from_form + savings.enter_savings
                if count_savings >= savings.enter_savings:
                    savings.new_savings = savings.enter_savings
                else:
                    savings.new_savings = savings.enter_savings - daily_expanse_from_form + unxpected_income_form_form

            savings.new_all_unregular_expese_you_may_spend = all_unregular_expese_you_may_spend
            savings.save()

            return redirect('sum/sumapp:daily-calculation', id = request.user.id)


class RaportView(LoginRequiredMixin, View):
    def get(self, request, id):
        user = User.objects.get(id = id)
        monthly_steady_income = MonthlyIncome.objects.get(user_id=id)
        mon_steady_in = monthly_steady_income.income
        monthly_steady_expense = MonthlyExpense.objects.get(user_id=id)
        mon_steady_ex = monthly_steady_expense.expense
        unregular_monthly_expense = UnregularExpense.objects.get(user_id=id)
        un_monthly_ex = unregular_monthly_expense.expense
        additional_income_expense = IncomeExpense.objects.filter(user_id=id)

        additional_exepense_result = 0
        for additional_exepense in additional_income_expense:
            if additional_exepense.additional_expense:
                additional_exepense_result += additional_exepense.additional_expense

        additional_income_expense = IncomeExpense.objects.filter(user_id=id)
        addittional_income_result = 0
        for addittional_income in additional_income_expense:
            if addittional_income.additional_income:
                addittional_income_result += addittional_income.additional_income

        real_unregular_expense = additional_exepense_result

        income_expense = IncomeExpense.objects.filter(user_id = user.id).order_by('-expense_date')
        ctx = {'mon_in':mon_steady_in,
               'mon_ex':mon_steady_ex,
               'un_ex': un_monthly_ex,
               'real_un_ex': real_unregular_expense,
                'income_expense': income_expense,
               'un_in': addittional_income_result,
               'user':user}

    # podpiać w html pod hedery tablicy filtry do różnych zestawień  i zrobić do nich htlme i widoki i url
        return render(request, 'sumapp/raport.html', ctx)

class ModifyRaportView(LoginRequiredMixin, View):
    def get(self, request, id):
        form = ResumeForm()
        user = User.objects.get(id = id)
        monthly_steady_income = MonthlyIncome.objects.get(user_id=id)
        mon_steady_in = monthly_steady_income.income
        monthly_steady_expense = MonthlyExpense.objects.get(user_id=id)
        mon_steady_ex = monthly_steady_expense.expense
        unregular_monthly_expense = UnregularExpense.objects.get(user_id=id)
        un_monthly_ex = unregular_monthly_expense.expense
        additional_income_expense = IncomeExpense.objects.filter(user_id=id)

        additional_exepense_result = 0
        for additional_exepense in additional_income_expense:
            if additional_exepense.additional_expense:
                additional_exepense_result += additional_exepense.additional_expense

        additional_income_expense = IncomeExpense.objects.filter(user_id=id)
        addittional_income_result = 0
        for addittional_income in additional_income_expense:
            if addittional_income.additional_income:
                addittional_income_result += addittional_income.additional_income

        real_unregular_expense = additional_exepense_result

        income_expense = IncomeExpense.objects.filter(user_id = user.id).order_by('-expense_date')
        ctx = {'mon_in':mon_steady_in,
               'mon_ex':mon_steady_ex,
               'un_ex': un_monthly_ex,
               'real_un_ex': real_unregular_expense,
                'income_expense': income_expense,
               'un_in': addittional_income_result,
               'user':user,
               'form':form}
        return render(request, 'sumapp/modify-delete-records.html', ctx)
    def post(self, request,id):
        form = ResumeForm(request.POST)
        if form.is_valid():
            return redirect('sum/sumapp:daily-calculation', id = request.user.id)

class GeneratePdfView(LoginRequiredMixin, View):
    def get(self, request, id):
        user = User.objects.get(id=id)
        monthly_steady_income = MonthlyIncome.objects.get(user_id=id)
        mon_steady_in = monthly_steady_income.income
        monthly_steady_expense = MonthlyExpense.objects.get(user_id=id)
        mon_steady_ex = monthly_steady_expense.expense
        unregular_monthly_expense = UnregularExpense.objects.get(user_id=id)
        un_monthly_ex = unregular_monthly_expense.expense
        additional_income_expense = IncomeExpense.objects.filter(user_id=id)

        additional_exepense_result = 0
        for additional_exepense in additional_income_expense:
            if additional_exepense.additional_expense:
                additional_exepense_result += additional_exepense.additional_expense

        additional_income_expense = IncomeExpense.objects.filter(user_id=id)
        addittional_income_result = 0
        for addittional_income in additional_income_expense:
            if addittional_income.additional_income:
                addittional_income_result += addittional_income.additional_income

        real_unregular_expense = additional_exepense_result

        income_expense = IncomeExpense.objects.filter(user_id=user.id).order_by('-expense_date')
        ctx = {'mon_in': mon_steady_in,
               'mon_ex': mon_steady_ex,
               'un_ex': un_monthly_ex,
               'real_un_ex': real_unregular_expense,
               'income_expense': income_expense,
               'un_in': addittional_income_result,
               'user': user}
        pdf = render_to_pdf('sumapp/raport-pdf.html', ctx)
        return HttpResponse(pdf, content_type='application/pdf')


class RaportSendView(LoginRequiredMixin, View):
     def get(self, request, id):
            ctx = {'form': MailForm()}
            return  render(request, 'sumapp/raport-send-mail.html',ctx)
     def post(self, request, id):
         form = MailForm(request.POST)
         if form.is_valid():
             user = User.objects.get(id=id)
             monthly_steady_income = MonthlyIncome.objects.get(user_id=id)
             mon_steady_in = monthly_steady_income.income
             monthly_steady_expense = MonthlyExpense.objects.get(user_id=id)
             mon_steady_ex = monthly_steady_expense.expense
             unregular_monthly_expense = UnregularExpense.objects.get(user_id=id)
             un_monthly_ex = unregular_monthly_expense.expense
             additional_income_expense = IncomeExpense.objects.filter(user_id=id)

             additional_exepense_result = 0
             for additional_exepense in additional_income_expense:
                 if additional_exepense.additional_expense:
                     additional_exepense_result += additional_exepense.additional_expense

             additional_income_expense = IncomeExpense.objects.filter(user_id=id)
             addittional_income_result = 0
             for addittional_income in additional_income_expense:
                 if addittional_income.additional_income:
                     addittional_income_result += addittional_income.additional_income

             real_unregular_expense = additional_exepense_result

             income_expense = IncomeExpense.objects.filter(user_id=user.id).order_by('-expense_date')
             ctx = {'mon_in': mon_steady_in,
                    'mon_ex': mon_steady_ex,
                    'un_ex': un_monthly_ex,
                    'real_un_ex': real_unregular_expense,
                    'income_expense': income_expense,
                    'un_in': addittional_income_result,
                    'user':user}

             mail_adress_from_form = form.cleaned_data['mail_adress']
             mail_from = getattr(settings, 'DEFAULT_EMAIL', "")
             html_message = render_to_string('sumapp/raport.html', ctx)
             plain_message = strip_tags(html_message)
             send_mail('raport z aplikacji "SUM"', plain_message, mail_from, [mail_adress_from_form], html_message=html_message)
             url = reverse('sum/sumapp:daily-calculation', kwargs={'id': user.id})
             return redirect(url)
         return render(request, 'sumapp/raport-send-mail.html', {'form':form})


class ResumeView(LoginRequiredMixin, View):
    def get(self, request, id):
        form = ResumeForm()
        monthly_income = MonthlyIncome.objects.get(user_id = id)
        monthly_steady_expense = MonthlyExpense.objects.get(user_id = id)
        monthly_delerated_unregular_expense = UnregularExpense.objects.get(user_id = id)
        dream = Dream.objects.get(user_id = id)
        dream_price = dream.price
        unregular_monthly_expense = UnregularExpense.objects.get(user_id = id)
        un_monthly_ex = unregular_monthly_expense.expense

        additional_income_expense = IncomeExpense.objects.filter(user_id=id)
        additional_exepense_result = 0
        for additional_exepense in additional_income_expense:
            if additional_exepense.additional_expense:
                additional_exepense_result += additional_exepense.additional_expense
            all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result

        additional_income_expense = IncomeExpense.objects.filter(user_id=id)
        addittional_income_result = 0
        for addittional_income in additional_income_expense:
            if addittional_income.additional_income:
                addittional_income_result += addittional_income.additional_income
            all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result + addittional_income_result


        savings = SteadyData.objects.get(user_id = id)
        savings.monthly_savings = savings.new_savings + all_unregular_expese_you_may_spend

        if savings.monthly_savings >= dream_price:
            messages.info(request, 'BRAWO !!! GRATULACJE !!! UDAŁO CI SIĘ UZBIERAĆ NA SWOJE MARZENIE !')
        else:
            messages.info(request, 'Musisz jeszcze trochę uzbierać by spełnić swoje marzenie. SUM trzyma za Ciebie kciuki!')

        ctx = {'monthly_income':monthly_income.income,
                'monthly_steady_expense':monthly_steady_expense.expense,
                'mothly_delerateted_expense':monthly_delerated_unregular_expense.expense,
                'new_savings': savings.monthly_savings,
               'all_unregular_expense': additional_exepense_result,
               'all_unxpected_income' : addittional_income_result,
               'dream' : dream,
               'price' : dream_price,
               'form':form
               }
        return render (request, 'sumapp/resume.html', ctx)
    def post(self, request, id):
        form = ResumeForm(request.POST)
        if form.is_valid():
            savings = SteadyData.objects.get(user_id=id)
            unregular_monthly_expense = UnregularExpense.objects.get(user_id=id)
            un_monthly_ex = unregular_monthly_expense.expense

            additional_income_expense = IncomeExpense.objects.filter(user_id=id)
            additional_exepense_result = 0
            for additional_exepense in additional_income_expense:
                if additional_exepense.additional_expense:
                    additional_exepense_result += additional_exepense.additional_expense
                all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result

            additional_income_expense = IncomeExpense.objects.filter(user_id=id)
            addittional_income_result = 0
            for addittional_income in additional_income_expense:
                if addittional_income.additional_income:
                    addittional_income_result += addittional_income.additional_income
                all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result + addittional_income_result

            savings.monthly_savings = savings.new_savings + all_unregular_expese_you_may_spend
            savings.save()
            url = reverse('sum/sumapp:query-update', kwargs={'user_id': id})
            return redirect(url)


class ModifyRecordView(LoginRequiredMixin, View):
    def get(self,request, id):
        in_ex = IncomeExpense.objects.get(id = id)
        form = DailyCalculationForm(initial={
                'daily_expanse': in_ex. additional_expense,
                'for_what': in_ex.expense_object,
                'category' : in_ex.category.name,
                'date_expanse': in_ex.expense_date,
                'unxpected_income': in_ex.additional_income,
                'from_who': in_ex.source_income,
                'date_income': in_ex.income_date})

        messages.info(request, 'Modyfikuj wpis i zapisz')
        return render(request, 'sumapp/modify-record.html', {'form':form})
    def post(self, request, id):
        form = DailyCalculationForm(request.POST)
        if form.is_valid():
            in_ex = IncomeExpense.objects.get(id=id)
            user = in_ex.user_id
            daily_expanse_from_form = form.cleaned_data['daily_expanse']
            for_what_from_form = form.cleaned_data['for_what']
            category_from_form = form.cleaned_data['category']
            date_income_from_form = form.cleaned_data['date_income']
            unxpected_income_form_form = form.cleaned_data['unxpected_income']
            from_who_form_form = form.cleaned_data['from_who']
            date_expanse_form_form = form.cleaned_data['date_expanse']
            new_category_for_now_record = Category.objects.get(id = id)
            new_category_for_now_record.name = category_from_form
            new_category_for_now_record.save()

            new_category = Category.objects.get(id = id)

            in_ex.additional_income=unxpected_income_form_form
            in_ex.additional_expense=daily_expanse_from_form
            in_ex.income_date=date_income_from_form
            in_ex.category = new_category
            in_ex.expense_date=date_expanse_form_form
            in_ex.source_income=from_who_form_form
            in_ex.expense_object=for_what_from_form
            in_ex.user_id = in_ex.user_id
            in_ex.save()

            unregular_monthly_expense = UnregularExpense.objects.get(user_id = user)
            un_monthly_ex = unregular_monthly_expense.expense
            additional_income_expense = IncomeExpense.objects.filter(user_id=user)
            additional_exepense_result = 0
            for additional_exepense in additional_income_expense:
                if additional_exepense.additional_expense:
                    additional_exepense_result += additional_exepense.additional_expense
                all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result

            additional_income_expense = IncomeExpense.objects.filter(user_id=user)
            addittional_income_result = 0
            for addittional_income in additional_income_expense:
                if addittional_income.additional_income:
                    addittional_income_result += addittional_income.additional_income
                all_unregular_expese_you_may_spend = un_monthly_ex - additional_exepense_result + addittional_income_result

            savings = SteadyData.objects.get(user_id=user)

            if all_unregular_expese_you_may_spend <= 0 and (
                    -1 * all_unregular_expese_you_may_spend) <= savings.enter_savings:
                conut_expense = (-1 * all_unregular_expese_you_may_spend)
                savings.new_savings = savings.enter_savings - conut_expense

            if (-1 * all_unregular_expese_you_may_spend) > savings.enter_savings:
                conut_expense = (-1 * all_unregular_expese_you_may_spend)
                savings.new_savings = savings.enter_savings - conut_expense

            if all_unregular_expese_you_may_spend > 0:
                count_savings = daily_expanse_from_form + savings.enter_savings
                if count_savings >= savings.enter_savings:
                    savings.new_savings = savings.enter_savings
                else:
                    savings.new_savings = savings.enter_savings - daily_expanse_from_form + unxpected_income_form_form

            savings.new_all_unregular_expese_you_may_spend = all_unregular_expese_you_may_spend
            savings.save()

        return redirect('sum/sumapp:daily-calculation', id = in_ex.user_id)


class DeleteRecordView(LoginRequiredMixin, View):
    def get(self, request, id):
       in_ex = IncomeExpense.objects.get(id = id)
       form = ReturnForm()
       ctx = {  'daily_expanse': in_ex. additional_expense,
                'for_what': in_ex.expense_object,
                'date_expanse': in_ex.expense_date,
                'unxpected_income': in_ex.additional_income,
                'from_who': in_ex.source_income,
                'date_income': in_ex.income_date,
                'form':form
            }
       messages.info(request, 'Na pewno chcesz usunąć ten wpis? ')
       return render(request, 'sumapp/delete-record.html', ctx)

    def post(self, request, id):
        form = ReturnForm(request.POST)
        if form.is_valid():
            in_ex = IncomeExpense.objects.get(id=id)
            user = in_ex.user_id
            unregular_monthly_expense = UnregularExpense.objects.get(user_id=user)
            un_monthly_ex = unregular_monthly_expense.expense
            additional_income_expense = IncomeExpense.objects.filter(user_id=user)
            additional_exepense_result = 0
            for additional_exepense in additional_income_expense:
                if additional_exepense.additional_expense:
                    additional_exepense_result += additional_exepense.additional_expense
                ad_ex_result = additional_exepense_result- in_ex.additional_expense
                all_unregular_expese_you_may_spend = un_monthly_ex - ad_ex_result

            additional_income_expense = IncomeExpense.objects.filter(user_id=user)
            addittional_income_result = 0
            for addittional_income in additional_income_expense:
                if addittional_income.additional_income:
                    addittional_income_result += addittional_income.additional_income
                ad_in_result = addittional_income_result - in_ex.additional_income
                all_unregular_expese_you_may_spend = un_monthly_ex - ad_ex_result + ad_in_result

            in_ex.delete()
            savings = SteadyData.objects.get(user_id=user)

            if all_unregular_expese_you_may_spend <= 0 and (
                    -1 * all_unregular_expese_you_may_spend) <= savings.enter_savings:
                conut_expense = (-1 * all_unregular_expese_you_may_spend)
                savings.new_savings = savings.enter_savings - conut_expense

            if (-1 * all_unregular_expese_you_may_spend) > savings.enter_savings:
                conut_expense = (-1 * all_unregular_expese_you_may_spend)
                savings.new_savings = savings.enter_savings - conut_expense

            if all_unregular_expese_you_may_spend > 0:
                count_savings = in_ex.additional_expense + savings.enter_savings
                if count_savings >= savings.enter_savings:
                    savings.new_savings = savings.enter_savings
                else:
                    savings.new_savings = savings.enter_savings + in_ex.additional_income - in_ex.additional_expense


            savings.new_all_unregular_expese_you_may_spend = all_unregular_expese_you_may_spend
            savings.save()

        return redirect('sum/sumapp:daily-calculation', id = in_ex.user_id)



class SessionIdleTimeout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        if request.user.is_authenticated():
            current_datetime = datetime.datetime.now()
            last_login = LastLogin.objects.get(user_id = request.user.id)
            if last_login.last_login:
                last = (current_datetime - last_login.last_login).seconds
                print(last)
                if last > 60:
                    logout(request)
                    print('test')
                    return redirect('sum/sumapp:index')





class CategoryRaportView(LoginRequiredMixin, View):
    def get(self, request, id):
        user = User.objects.get(id = id)
        categories = Category.objects.order_by('name')
        expenses = IncomeExpense.objects.filter(user_id = user.id)

        podroze = 0
        for ex in expenses:
            # print(ex.category.name)
            if ex.category.name == 2:
                podroze += ex.additional_expense

        inne = 0
        for ex in expenses:
            if ex.category.name == 1:
                inne += ex.additional_expense

        ubrania = 0
        for ex in expenses:
            if ex.category.name == 3:
                ubrania += ex.additional_expense

        rozrywka = 0
        for ex in expenses:
            if ex.category.name == 4:
                rozrywka += ex.additional_expense

        jedzenie = 0
        for ex in expenses:
            if ex.category.name == 5:
                jedzenie += ex.additional_expense

        elektronika = 0
        for ex in expenses:
            if ex.category.name == 6:
                elektronika += ex.additional_expense

        dzieci = 0
        for ex in expenses:
            if ex.category.name == 7:
                dzieci += ex.additional_expense

        zajęcia_dodatkowe = 0
        for ex in expenses:
            if ex.category.name == 8:
                zajęcia_dodatkowe += ex.additional_expense

        hobby = 0
        for ex in expenses:
            if ex.category.name == 9:
                hobby += ex.additional_expense

        dom = 0
        for ex in expenses:
            if ex.category.name == 10:
                dom += ex.additional_expense

        edukacja = 0
        for ex in expenses:
            if ex.category.name == 11:
                edukacja += ex.additional_expense

        samochod = 0
        for ex in expenses:
            if ex.category.name == 12:
                samochod += ex.additional_expense

        zwierzeta = 0
        for ex in expenses:
            if ex.category.name == 13:
                zwierzeta += ex.additional_expense

        zdrowie = 0
        for ex in expenses:
            if ex.category.name == 14:
                zdrowie += ex.additional_expense

        ctx = {"user": user,
            "categories":expenses,
               "ubrania":ubrania,
               "jedzenie":jedzenie,
               "rozrywka":rozrywka,
               "podroze":podroze,
               "inne":inne,
                "elektronika":elektronika,
                "dzieci":dzieci,
                "zajęcia_dodatkowe":zajęcia_dodatkowe,
                "hobby":hobby,
                "dom":dom,
                "edukacja":edukacja,
                "samochod":samochod,
                "zwierzeta":zwierzeta,
               "zdrowie":zdrowie
         }
        return render(request, 'sumapp/raport-category.html', ctx)

