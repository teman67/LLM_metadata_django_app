from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views import generic
from .models import Post



class PostList(generic.ListView):
    
    queryset = Post.objects.all()
    template_name = "post_list.html"

class Home(generic.ListView):
    
    queryset = Post.objects.all()
    template_name = "index.html"