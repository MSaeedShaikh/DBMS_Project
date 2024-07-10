from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import os

u_id = -1
is_manager = False
IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
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
        items = list()
        for item in all_items:
            item = list(item)
            cursor.execute("SELECT * FROM get_img(%s)",[item[0]])
            images_temp = list(cursor.fetchall())
            images = list(zip(range(len(images_temp)), [row[1] for row in images_temp]))
            item.append(images)
            items.append(item)
        return render(request, "home.html", {'u_id':u_id, 'is_manager':is_manager, 'items':items})

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

def update_item(request, pk):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            cursor.execute("SELECT i_id, name, descrip, price, stock FROM items WHERE i_id=%s", [pk])
            item = cursor.fetchone()
            if(item):
                if request.method == 'POST':
                    name = request.POST['name']
                    descrip = request.POST['descrip']
                    price = request.POST['price']
                    stock = request.POST['stock']
                    cursor.execute("CALL update_item(%s, %s, %s, %s, %s)", [pk, name, descrip, price, stock])
                    messages.success(request, "Item Updated Successfully")
                    return redirect('home')
                else:
                    return render(request, "update.html", {'u_id':u_id, 'is_manager': is_manager, 'item': item})
            else:
                messages.success(request, "No such item")
                return redirect('home')
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')
    
def delete_item(request, pk):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            cursor.execute("SELECT i_id, name, descrip, price, stock FROM items WHERE i_id=%s", [pk])
            item = cursor.fetchone()
            if(item):
                cursor.execute("DELETE FROM items WHERE i_id=%s", [pk])
                messages.success(request, "Item Deleted")
                return redirect('home')
            else:
                messages.success(request, "No such item")
                return redirect('home')
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')

def buy_item(request, pk):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(not is_manager):
            cursor.execute("SELECT i_id, name, descrip, price, stock FROM items WHERE i_id=%s", [pk])
            item = cursor.fetchone()
            if(item):
                if request.method == 'POST':
                    quantity = request.POST['quantity']
                    cursor.execute("CALL new_purchase(%s, %s, %s)", [u_id, pk, quantity])
                    messages.success(request, "Your Purchase Was Successful")
                    return redirect('home')
                else:
                    return render(request, "buy.html", {'u_id':u_id, 'is_manager': is_manager, 'item':item})
            else:
                messages.success(request, "No such item")
                return redirect('home')
        else:
            messages.success(request, "You are not a customer")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')
    
def new_item(request):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            if request.method == 'POST':
                name = request.POST['name']
                descrip = request.POST['descrip']
                price = request.POST['price']
                stock = request.POST['stock']
                cursor.execute("CALL new_item(%s, %s, %s, %s)", [name, descrip, price, stock])
                messages.success(request, "New Item Created Successfully")
                return redirect('home')    
            else:
                return render(request, "new.html", {'u_id':u_id, 'is_manager': is_manager})
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')

def view_records(request):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            cursor.execute("SELECT * FROM remaining_records")
            remaining = cursor.fetchall()
            cursor.execute("SELECT * FROM completed_records")
            completed = cursor.fetchall()
            return render(request, "records.html", {'u_id':u_id, 'is_manager': is_manager, 'remaining': remaining, 'completed': completed})
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')

def check_record(request, pk):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            cursor.execute("SELECT * FROM check_record(%s)", [pk]);
            if_exist = (cursor.fetchone())[0]
            if(if_exist):
                messages.success(request, "Record Has Been Processed")
                return redirect('records_page')
            else:
                messages.success(request, "No Such Valid Record")
                return redirect('records_page')
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')
    
def image_upload(request, pk):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            cursor.execute("SELECT name FROM items WHERE i_id=%s", [pk])
            res = (cursor.fetchone())
            name = res[0]
            i_id = pk
            if(name):
                if request.method == 'POST':
                    image = request.FILES['image']
                    image_name = image.name
                    img_type = image_name.rsplit('.', 1)[1]
                    if img_type in IMAGE_TYPES:
                        cursor.execute("SELECT * FROM img_upload(%s, %s)", [i_id, img_type])
                        file_name = cursor.fetchone()[0]
                        file_name = "market/website/static/uploads/"+file_name
                        os.makedirs(os.path.dirname(file_name), exist_ok=True)
                        with open(file_name, "wb+") as f:
                            for chunk in image.chunks():
                                f.write(chunk)
                        messages.success(request, "Image Uploaded Successfully")
                        return redirect('image_upload', pk = i_id)
                    else:
                        messages.success(request, "Invalid Image Type")
                        return redirect('image_upload', pk = i_id)
                else:
                    cursor.execute("SELECT * FROM get_img(%s)", [i_id])
                    images = cursor.fetchall()
                    return render(request, "image_up.html", {'u_id':u_id, 'is_manager': is_manager, 'i_id': pk, 'name':name, 'images': images})
            else:
                messages.success(request, "No Such Item")
                return redirect('home')
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')
    
def image_delete(request, img_id, i_id):
    global u_id
    global is_manager
    if ((u_id != -1)):
        if(is_manager):
            cursor.execute("SELECT * FROM images WHERE img_id = %s", [img_id])
            if_exist = cursor.fetchone()[0]
            if (if_exist != 0):
                cursor.execute('SELECT * FROM delete_img(%s)', [img_id])
                file_name = cursor.fetchone()[0]
                os.remove("market/website/static/uploads/"+file_name)
                messages.success(request, "Image Removed Successfully")
                return redirect('image_upload', pk = i_id)
            else:
                messages.success(request, "No Such Image")
                return redirect('image_upload', pk = i_id)
        else:
            messages.success(request, "You are not authorized to do that")
            return redirect('home')
    else:
        messages.success(request, "You must be logged in to do that")
        return redirect('home')