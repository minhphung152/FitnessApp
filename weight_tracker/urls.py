from django.urls import path

from . import views

app_name = 'weight_tracker'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('delete/<int:pk>', views.delete_log, name='delete_log'),

    path('set_goal/', views.set_goal, name='set_goal'),
    path('goal_detail/<int:pk>', views.goal_detail, name='goal_detail'),
    path('goal/<int:pk>/delete', views.delete_goal, name='delete_goal'),
    path('goal/<int:pk>/update', views.update_goal, name='update_goal'),

    path('weight-data/', views.weight_data, name='weight_data'),
    path('weight-chart/', views.weight_chart, name='weight_chart'),

    path('log_bmi/', views.log_bmi, name='log_bmi'),
    path('bmi/<int:pk>', views.bmi_detail, name='bmi_detail'),

    path('weight_logs/', views.weight_logs, name='weight_logs'), 
]