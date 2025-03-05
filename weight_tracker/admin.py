from django.contrib import admin

from .models import WeightLog, Goal, BMILog

admin.site.register(WeightLog)
admin.site.register(Goal)
admin.site.register(BMILog)