from django.db import models

from django.contrib.auth.models import User

class WeightLog(models.Model):
    created_by = models.ForeignKey(User, related_name='weights', on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField()
    
    def __str__(self):
        return f'{self.created_by} - {self.weight} lbs'
    
class Goal(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('maintenance', 'Maintenance'),
    ]
    WEEKLY_GOAL = [
        ('lose_1', 'Lose 1 pound per week'),
        ('lose_2', 'Lose 2 pounds per week'),
        ('gain_1', 'Gain 1 pound per week'),
        ('gain_2', 'Gain 2 pounds per week')
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=20, choices=GOAL_CHOICES)
    weekly_goal = models.CharField(max_length=50, choices=WEEKLY_GOAL)
    target_weight = models.FloatField()
    start_weight = models.FloatField()
    target_date = models.DateField(blank=True, null=True)

    def get_goal_type_display(self):
        return dict(self.GOAL_CHOICES).get(self.goal_type, 'Unknown')
    
    def get_weekly_goal_display(self):
        return dict(self.WEEKLY_GOAL).get(self.weekly_goal, 'Unknown')
    
    def __str__(self):
        return f'{self.created_by} - {self.goal_type} - {self.target_weight} lbs'

    def progress_percentage(self):
        if self.goal_type == 'weight_loss':
            total_weight_to_lose = self.start_weight - self.target_weight
            weight_lost = self.start_weight - self.created_by.weights.latest('date').weight
            return round((weight_lost / total_weight_to_lose) * 100, 2)
        elif self.goal_type == 'weight_gain':
            total_weight_to_gain = self.target_weight - self.start_weight
            weight_gained = self.created_by.weights.latest('date').weight - self.start_weight
            return round((weight_gained / total_weight_to_gain) * 100, 2)
        return 0 # maintain

class BMILog(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bmi_logs')
    date = models.DateField(blank=True, null=True)
    weight = models.FloatField() # in pounds
    height = models.FloatField() # in inches

    def calculate_bmi(self):
        # add a feature later to convert input in feet to inches
        return round((self.weight / (self.height ** 2)) * 703, 2)

    def interpret_bmi(self):
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 24.9:
            return 'Healthy Weight'
        elif bmi < 29.9:
            return 'Overweight'
        else:
            return 'Obese'
    
    def __str__(self):
        return f'{self.created_by} - {self.date} - BMI: {self.calculate_bmi():.2f}'