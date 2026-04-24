from django.shortcuts import render

def activity_log(request):
    return render(request, "activity_logs/activity_log.html")