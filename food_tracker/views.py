from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from .forms import FoodSearchForm
from .models import FoodItem, FoodEntry
from django.db.models import Q, F
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

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
    servings = request.POST.get('servings', 1)
    date = request.POST.get('date') or timezone.now().date()
    meal_type = request.POST.get('meal_type', 'all')

    # Get full details from USDA API
    url = f'https://api.nal.usda.gov/fdc/v1/food/{fdc_id}'
    params = {'api_key': settings.USDA_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        food_data = response.json()

        # Extract nutrients safely
        nutrients = {nutrient['nutrient'].get('name', ''): nutrient.get('amount', 0) for nutrient in food_data['foodNutrients']}

        # Create FoodItem
        food_item, created = FoodItem.objects.get_or_create(
            name=food_data['description'].title(),
            defaults={
                'brand': food_data.get('brandOwner', ''),
                'serving_size': get_serving_size(food_data),
                'calories': nutrients.get('Energy', 0),
                'protein': nutrients.get('Protein', 0),
                'carbohydrates': nutrients.get('Carbohydrate, by difference', 0),
                'fats': nutrients.get('Total lipid (fat)', 0),
                'created_by': request.user
            }
        )

        FoodEntry.objects.create(
            user=request.user,
            food_item=food_item,
            servings=servings,
            date=date,
            meal_type=meal_type
        )

        messages.success(request,
            f'Successfully saved {food_item.name} ({servings} serving(s))!')
    
    except requests.exceptions.RequestException:
        messages.error(request, 'Failed to fetch food data.')
    except Exception as e:
        messages.error(request, 'Failed to save food item.')
    
    return redirect('food_tracker:food_search')

@login_required
def food_log(request):
    # View mode (daily/all)
    view_mode = request.GET.get('view', 'daily')
    meal_filter = request.GET.get('meal', 'all')

    # Date handling for daily view
    selected_date = None
    if view_mode == 'daily':
        try:
            selected_date = timezone.datetime.strptime(
                request.GET.get('date'), '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            selected_date = timezone.now().date()
    
    # Sorting handling
    sort_mapping = {
        'date': 'date',
        '-date': '-date',
        'name': 'food_item__name',
        '-name': '-food_item__name',
        'calories': 'food_item__calories',
        '-calories': '-food_item__calories',
        'servings': 'servings',
        '-servings': '-servings'
    }

    # Handle date selection
    try:
        selected_date = timezone.datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    # Get and validate sort parameter
    sort_param = request.GET.get('sort', '-date')
    sort = sort_mapping.get(sort_param, '-date')  # Default to '-date'

    # Base queryset
    food_entries = FoodEntry.objects.filter(user=request.user)

    # Apply view mode filter
    if view_mode == 'daily':
        food_entries = food_entries.filter(date=selected_date)
    
    # Add meal filtering
    if meal_filter != 'all':
        food_entries = food_entries.filter(meal_type=meal_filter)
    
    # Apply sorting
    food_entries = food_entries.order_by(sort)

    # Date navigation
    previous_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    
    # Calculate totals
    total_calories = sum(entry.total_calories for entry in food_entries)
    total_entries = food_entries.count()
    
    return render(request, 'food_tracker/food_log.html', {
        'food_entries': food_entries,
        'total_calories': total_calories,
        'total_entries': total_entries,
        'meal_filter': meal_filter,
        'meal_choices': FoodEntry.MEAL_CHOICES,
        'current_sort': sort_param,  # Use original parameter for template
        'selected_date': selected_date,
        'previous_date': previous_date,
        'next_date': next_date,
        'is_default_sort': sort_param == '-date',
        'view_mode': view_mode
    })