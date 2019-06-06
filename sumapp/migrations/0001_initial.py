# Generated by Django 2.2.1 on 2019-06-05 11:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UnregularExpense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense', models.DecimalField(decimal_places=2, max_digits=6)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SteadyData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enter_savings', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('new_savings', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('enter_all_unregular_expese_you_may_spend', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('new_all_unregular_expese_you_may_spend', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('login_check', models.IntegerField()),
                ('monthly_savings', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyIncome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('income', models.DecimalField(decimal_places=2, max_digits=8)),
                ('income_date', models.DateField(default=datetime.date(2019, 6, 5))),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyExpense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense', models.DecimalField(decimal_places=2, max_digits=8)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IncomeExpense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_income', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('additional_expense', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('income_date', models.DateTimeField(default=datetime.datetime.now)),
                ('expense_date', models.DateTimeField(default=datetime.datetime.now)),
                ('source_income', models.CharField(max_length=30)),
                ('expense_object', models.CharField(max_length=30)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dream', models.CharField(max_length=120)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.IntegerField(choices=[(1, 'inne'), (2, 'rozrywka'), (3, 'podróże'), (4, 'samochód'), (5, 'dzieci'), (6, 'zajęcia dodatkowe'), (7, 'edukacja'), (8, 'transport'), (9, 'dom'), (10, 'prezety'), (11, 'hobby'), (12, 'inne zakupy'), (13, 'jedzenie'), (14, 'ubrania'), (15, 'elektronika')])),
                ('expense', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='sumapp.IncomeExpense')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
