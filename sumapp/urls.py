from django.urls import path
from sumapp import views



app_name = 'sum/sumapp'

urlpatterns = [
    path('', views.StartPageView.as_view(), name = 'start'),
    path('login', views.LoginNewView.as_view(), name = 'index'),
    path('registration', views.AddUserView.as_view(), name='registration'),
    path('query/<int:user_id>', views.QueryView.as_view(), name = 'query'),
    path('query_update/<int:user_id>', views.QueryUpdateView.as_view(), name = 'query-update'),
    path('logout', views.LogoutView.as_view(), name = 'logout'),
    path('calculation/<int:id>', views.CalculationView.as_view(), name = 'calculation'),
    path('daily_calculation/<int:id>', views.DailyCalculation.as_view(), name = 'daily-calculation'),
    path('raport/<int:id>', views.RaportView.as_view(), name = 'raport'),
    path('pdf/<int:id>', views.GeneratePdfView.as_view(), name = 'pdf'),
    path('mail/<int:id>', views.RaportSendView.as_view(), name = 'mail'),
    path('resume/<int:id>', views.ResumeView.as_view(), name = 'resume'),
    path('modify_record/<int:id>',views.ModifyRecordView.as_view(), name = 'modify-record'),
    path('delete_record/<int:id>', views.DeleteRecordView.as_view(), name = "delete-record"),
    path('modify_raport/<int:id>', views.ModifyRaportView.as_view(), name = 'modify-raport'),
    path('raport-category/<int:id>',views.CategoryRaportView.as_view(), name = 'raport-category')

]