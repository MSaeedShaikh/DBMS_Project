from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

u_id = -1
cursor = connection.cursor()

# Create your views here.
def home(request):
    global u_id
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        cursor.execute("SELECT * FROM authenticate(%s, %s)", [email, password])
        u_id = (cursor.fetchone())[0]
        print(u_id)
        if u_id != -1:
            messages.success(request, "You Have Been Logged In")
            return redirect('home')
        else:
            messages.success(request, "Incorrect Email or Password")
            return redirect('home')
    else:
        return render(request, "home.html", {'u_id':u_id})

def logout_user(request):
    global u_id
    u_id = -1
    messages.success(request, "You Have Been Logged Out")
    return redirect('home')