from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages


def home(request):
    return render(request, 'home.html')