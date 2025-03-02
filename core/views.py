from django.shortcuts import render, redirect

from tracker.models import WeightLog, Goal, BMILog

from .forms import SignupForm

# Render the index
def index(request):
    return render(request, 'core/index.html')

# Render weight tracker page
# def weight_tracker(request):
#     logs = WeightLog.objects.filter(created_by=request.user).order_by('-date', '-id')
#     goal = Goal.objects.filter(created_by=request.user).last() # get the latest goal
#     bmi_logs = BMILog.objects.filter(created_by=request.user)

#     latest_log = None
#     if logs:
#         latest_log = logs.first().weight
    
#     return render(request, 'core/weight_tracker.html', {
#         'goal': goal,
#         'latest_log': latest_log,
#         'logs': logs,
#         'bmi_logs': bmi_logs,
#         })

# Handle user sign up
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form,
    })