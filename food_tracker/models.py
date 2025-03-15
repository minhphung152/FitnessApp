from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    serving_size = models.CharField(max_length=100) # 1 cup, 1 oz, 1 slice, 100 grams etc.
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=1) # grams
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=1)
    fats = models.DecimalField(max_digits=5, decimal_places=1)
    fiber = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    sugar = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Food Items'

    def __str__(self):
        return f'{self.name} ({self.serving_size})'

class FoodEntry(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    date = models.DateField()
    servings = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    meal_type = models.CharField(
        max_length=9,
        choices=MEAL_CHOICES,
    )

    class Meta: 
        verbose_name_plural = 'Food Entries'

    @property
    def total_calories(self):
        return self.servings * self.food_item.calories

    @property
    def total_protein(self):
        return self.servings * self.food_item.protein