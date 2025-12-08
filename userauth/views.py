from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegisterForm, LoginForm
# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('index')   
    else:
            form = RegisterForm()

    context = {
        'form': form
    }        
    return render(request, 'userauth/register.html', context)        

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('index')
    else:
            form = LoginForm()
    
    context ={
        'form': form
    }

    return render(request, 'userauth/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')