from django import forms

from .models import WeightLog, Goal, BMILog

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border'

class NewWeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ('weight', 'date', )
    
        widgets = {
            'weight': forms.TextInput(attrs={
                'placeholder': 'Enter weight in lbs',
                'class': INPUT_CLASSES,
            }), 
            'date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'Enter date',
                'class': INPUT_CLASSES,
            }),
        }

class EditWeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ('weight', )
    
        widgets = {
            'weight': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
            }), 
        }

class SetGoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ('goal_type', 'weekly_goal', 'start_weight', 'target_weight',)

        widgets = {
            'goal_type': forms.Select(attrs={
                'class': INPUT_CLASSES,
            }),
            'weekly_goal': forms.Select(attrs={
                'class': INPUT_CLASSES,
            }),
            'start_weight': forms.TextInput(attrs={
                'placeholder': 'Enter weight in lbs',
                'class': INPUT_CLASSES,
            }),
            'target_weight': forms.TextInput(attrs={
                'placeholder': 'Enter weight in lbs',
                'class': INPUT_CLASSES,
            }),
            # 'target_date': forms.DateInput(attrs={
            #     'type': 'date',
            #     'class': INPUT_CLASSES,
            # })
        }

class HeightField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(min_value=0, label='Feet'),
            forms.IntegerField(min_value=0, label='Inches'),
        )
        super().__init__(fields, *args, **kwargs)
    
    def compress(self, data_list):
        if data_list:
            feet = data_list[0]
            inches = data_list[1]
            total_inches = (feet * 12) + inches
            return total_inches
        return None
    
class HeightWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.NumberInput(attrs={
                'placeholder': 'Feet',
                'class': 'border rounded-xl px-4 py-2 w-24',
                'min': 0,
                'max': 8,
            }),
            forms.NumberInput(attrs={
                'placeholder': 'Inches',
                'class': 'border rounded-xl px-4 py-2 w-24', 
                'min': 0,
                'max': 11,
            }),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value: 
            feet = value // 12
            inches = value % 12
            return [feet, inches]
        return [0, 0]

class BMILogForm(forms.ModelForm):
    height = HeightField(widget=HeightWidget())

    class Meta:
        model = BMILog
        fields = ('weight', 'height', )
        widgets = {
            # 'date': forms.DateInput(attrs={
            #     'type': 'date',
            #     'class': INPUT_CLASSES
            # }),
            'weight': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
            }),
        }