from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from .forms import FoodSearchForm
from .models import FoodItem
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib import messages

def search_usda_foods(query):
    url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'api_key': settings.USDA_API_KEY,
        'query': query,
        'pageSize': 10,
        'dataType': 'Survey (FNDDS)'
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return parse_usda_response(response.json())
    except requests.exceptions.RequestException as e:
        print(f'USDA API Error: {e}')
        return []

def parse_usda_response(data):
    foods = []
    for food in data.get('foods', []):
        nutrients = {n['nutrientName']: n['value'] for n in food.get('foodNutrients', [])}

        food_data = {
            'fdc_id': food['fdcId'],
            'name': food['description'].title(),
            'brand': food.get('brandOwner', ''),
            'serving_size': get_serving_size(food),
            'calories': nutrients.get('Energy', 0),
            'protein': nutrients.get('Protein', 0),
            'carbs': nutrients.get('Carbohydrate, by difference', 0),
            'fats': nutrients.get('Total lipid (fat)', 0),
            'fiber': nutrients.get('Fiber, total dietary', 0),
            'sugar': nutrients.get('Sugars, total including NLEA', 0),
            'source': 'USDA'
        }
        foods.append(food_data)
    return foods

def get_serving_size(food):
    if 'servingSize' in food and 'servingSizeUnit' in food:
        return f"{food['servingSize']} {food['servingSizeUnit']}"
    return 'N/A'

@login_required
def food_search(request):
    results = []
    usda_results = []

    if request.method == 'POST':
        form = FoodSearchForm(request.POST)
        if form.is_valid():
            # Search local database
            query = form.cleaned_data['search']
            results = FoodItem.objects.filter(
                Q(name__icontains=query) | Q(brand__icontains=query)
            )

            # Search USDA database
            usda_results = search_usda_foods(query)
    else:
        form = FoodSearchForm()
    
    return render(request, 'food_tracker/food_search.html', {
        'form': form,
        'results': results,
        'usda_results': usda_results
    })

@require_POST
@login_required
def save_usda_food(request):
    fdc_id = request.POST.get('fdc_id')

    # Get full details from USDA API
    url = f'https://api.nal.usda.gov/fdc/v1/food/{fdc_id}'
    params = {'api_key': settings.USDA_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        food_data = response.json()

        # Extract nutrients safely
        nutrients = {n['nutrientName']: n['value'] for n in food_data.get('foodNutrients', []) if 'nutrientName' in n}

        # Create FoodItem
        food = FoodItem(
            name=food_data['description'].title(),
            brand=food_data.get('brandOwner', ''),
            serving_size=get_serving_size(food_data),
            calories=nutrients.get('Energy', 0),
            protein=nutrients.get('Protein', 0),
            carbohydrates=nutrients.get('Carbohydrate, by difference', 0),
            fats=nutrients.get('Total lipid (fat)', 0),
            created_by=request.user
        )
        food.save()

        messages.success(request, f'{food.name} added to database!')
    
    except Exception as e:
        messages.error(request, 'Failed to save food item.')
        print(f'USDA API Error: {e}')
    
    return redirect('food_tracker:food_search')
