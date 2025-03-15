from django.urls import path
from . import views

app_name = 'food_tracker'

urlpatterns = [
    path('foods', views.food_search, name='food_search'),
    path('save_usda_food', views.save_usda_food, name='save_usda_food'),
    path('food-log', views.food_log, name='food_log'),
]