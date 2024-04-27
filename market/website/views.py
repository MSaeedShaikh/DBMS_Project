from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

u_id = -1
is_manager = False
cursor = connection.cursor()

# Create your views here.
def home(request):
    global u_id
    global is_manager
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        cursor.execute("SELECT * FROM authenticate(%s, %s)", [email, password])
        u_id = int((cursor.fetchone())[0])
        cursor.execute("SELECT * FROM check_manager(%s)", [u_id])
        is_manager = (cursor.fetchone())[0]
        if u_id != -1:
            messages.success(request, "You Have Been Logged In")
            return redirect('home')
        else:
            messages.success(request, "Incorrect Email or Password")
            return redirect('home')
    else:
        cursor.execute("SELECT i_id, name, descrip, price, stock FROM items")
        all_items = cursor.fetchall()
        return render(request, "home.html", {'u_id':u_id, 'is_manager':is_manager, 'items':all_items})

def logout_user(request):
    global u_id
    u_id = -1
    messages.success(request, "You Have Been Logged Out")
    return redirect('home')

def register_user(request):
    global u_id
    global is_manager
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
                u_id = int((cursor.fetchone())[0])
                cursor.execute("SELECT * FROM check_manager(%s)", [u_id])
                is_manager = (cursor.fetchone())[0]
                messages.success(request, "You Have Been Registered")
                return redirect('home')
        else:
            return render(request, "register.html", {'u_id':u_id, 'is_manager': is_manager})
    else:
        messages.success(request, "You Are Already Registered")
        return redirect('home')
