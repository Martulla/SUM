
from django.contrib import admin

from sumapp import models

admin.site.register(models.MonthlyExpense)
admin.site.register(models.UnregularExpense)
admin.site.register(models.MonthlyIncome)
admin.site.register(models.IncomeExpense)
admin.site.register(models.Dream)

