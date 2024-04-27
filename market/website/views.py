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

def register_user(request):
    global u_id
    if(u_id == -1):
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            name = request.POST['name']
            phone = request.POST['phone']
            status = request.POST['status']
            is_manager = (status == "Manager")
            cursor.execute("SELECT * FROM check_valid_user(%s)", [email])
            valid = (cursor.fetchone())[0]
            if (valid == 0):
                messages.success("Email Already In Use")
                return redirect('register')
            else:
                cursor.execute("CALL new_user(%s, %s, %s, %s, %s)", [name, email, password, phone, is_manager])
                cursor.execute("SELECT * FROM authenticate(%s, %s)", [email, password])
                u_id = (cursor.fetchone())[0]
                messages.success(request, "You Have Been Registered")
                return redirect('home')
        else:
            return render(request, "register.html", {'u_id':u_id})
    else:
        messages.success(request, "You Are Already Registered")
        return redirect('home')
