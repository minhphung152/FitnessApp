from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from .forms import NewWeightLogForm, SetGoalForm, BMILogForm
from .models import WeightLog, Goal, BMILog

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# Render index page of weight tracker app
@login_required
def index(request):
    logs = WeightLog.objects.filter(created_by=request.user).order_by('-date', '-id')
    goal = Goal.objects.filter(created_by=request.user).last() # get the latest goal
    bmi_logs = BMILog.objects.filter(created_by=request.user)

    latest_log = None
    if logs:
        latest_log = logs.first().weight
    
    # Weight chart data (last 30 days)
    weight_start_date = timezone.now().date() - relativedelta(days=30)
    weight_data = WeightLog.objects.filter(
        created_by=request.user,
        date__gte=weight_start_date
    ).order_by('date')

    context = {
        'goal': goal,
        'latest_log': latest_log,
        'logs': logs,
        'bmi_logs': bmi_logs,
        'weight_labels': [entry.date.strftime('%Y-%m-%d') for entry in weight_data],
        'weight_values': [float(entry.weight) for entry in weight_data],
    }
    
    return render(request, 'weight_tracker/index.html', context)

# All weight logs
@login_required
def weight_logs(request):
    logs = WeightLog.objects.filter(created_by=request.user).order_by('date')
    latest_log = None
    if logs:
        latest_log = logs.first().weight
    
    return render(request, 'weight_tracker/weight_logs.html', {
        'logs': logs,
        'latest_log': latest_log,
    })

# Goal detail
@login_required
def goal_detail(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    try:
        current_weight = goal.created_by.weights.latest('date').weight
    except WeightLog.DoesNotExist:
        current_weight = None

    return render(request, 'weight_tracker/goal.html', {
        'current_weight': current_weight,
        'goal': goal,
    })

# Log new weight
@login_required
def new(request):
    if request.method == 'POST':
        form = NewWeightLogForm(request.POST, request.FILES)

        if form.is_valid():
            weight_log = form.save(commit=False)
            weight_log.created_by = request.user
            weight_log.save()

            return redirect('weight_tracker:index')
    else:
        form = NewWeightLogForm()

    return render(request, 'weight_tracker/form.html', {
        'form': form,
        'title': 'New Weight Log',
    })

# Set new goal
@login_required
def set_goal(request):
    if request.method == 'POST':
        form = SetGoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = request.user
            goal.save()

            return redirect('weight_tracker:index')
    else:
        form = SetGoalForm()

    return render(request, 'weight_tracker/form.html', {
        'form': form,
        'title': 'Set Goal',
    })

# Update goal
@login_required
def update_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    if request.method == 'POST':
        form = SetGoalForm(request.POST, instance=goal)

        if form.is_valid():
            form.save()
            return redirect('weight_tracker:index')
    else:
        form = SetGoalForm(instance=goal)
    return render(request, 'weight_tracker/update_goal.html', {
        'form': form,
        'goal': goal,
    })

# Delete weight log
@login_required
def delete_log(request, pk):
    log = get_object_or_404(WeightLog, pk=pk, created_by=request.user)
    log.delete()

    return redirect('weight_tracker:weight_logs')

# Delete goal
@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(Goal, pk=pk, created_by=request.user)
    goal.delete()

    return redirect('weight_tracker:index')

# Weight Trends Chart
@login_required
def weight_data(request):
    weight_logs = WeightLog.objects.filter(created_by=request.user).order_by('date')
    goal = Goal.objects.filter(created_by=request.user).first() # Assuming one goal per user
    target_weight = goal.target_weight if goal else None

    data = {
        'dates': [log.date.strftime('%Y-%m-%d') for log in weight_logs],
        'weights': [log.weight for log in weight_logs],
        'target_weight': target_weight,
    }
    return JsonResponse(data)

@login_required
def weight_chart(request):
    return render(request, 'weight_tracker/weight_chart.html')


# BMI Tracker
@login_required
def log_bmi(request):
    if request.method == 'POST':
        form = BMILogForm(request.POST)
        if form.is_valid():
            bmi_log = form.save(commit=False)
            bmi_log.created_by = request.user
            bmi_log.save()
            return redirect('weight_tracker:bmi_detail', pk=bmi_log.pk)
    else:
        form = BMILogForm()
    return render(request, 'weight_tracker/log_bmi.html', {
        'form': form,
    })

# BMI detail
@login_required
def bmi_detail(request, pk):
    bmi_log = BMILog.objects.get(pk=pk, created_by=request.user)
    bmi = bmi_log.calculate_bmi()
    status = bmi_log.interpret_bmi()

    feet, inches = divmod(bmi_log.height, 12)
    height = f"{int(feet)}'{int(inches)}"
    return render(request, 'weight_tracker/bmi_detail.html', {
        'bmi_log': bmi_log, 
        'bmi': bmi,
        'height': height,
        'status': status,
    })