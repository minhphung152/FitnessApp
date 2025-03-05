from django import forms

class FoodSearchForm(forms.Form):
    search = forms.CharField(label='Search Foods', max_length=255)    