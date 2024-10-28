from django.shortcuts import render
from .models import Exam

def home(request):
    exams = Exam.objects.all()
    context = {'exams' : exams}
    return  render(request, 'home.html', context)