from django.shortcuts import render

def list_activities(request):
    return render(request, "activity_logs/index.html")