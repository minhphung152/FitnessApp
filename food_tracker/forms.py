from django import forms
from .models import FoodEntry

class FoodSearchForm(forms.Form):
    search = forms.CharField(label='Search Foods', max_length=255) 

class FoodEntryForm(forms.ModelForm):
    class Meta:
        model = FoodEntry
        fields = ['date', 'food_item', 'servings', 'meal_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }