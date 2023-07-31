from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from . models import Room , Topic , Message
from .forms import RoomForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request,'User does not exist')

        user = authenticate(request , username = username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Username OR password does not exit')

    context = {
        'page':page
    }
    return render(request, 'login_register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    context = {
        'form':form
    }
    return render(request,'login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    all_rooms = Room.objects.all().count()
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        )
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'rooms':rooms,
        'topics':topics,
        'room_messages':room_messages,
        'all_rooms':all_rooms
               }
    return render(request,'home.html',context)

def room(request,pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all().order_by('-created')
    participants=room.participants.all()
    if request.method == 'POST':    
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        'room':room,
        'room_messages':room_messages,
        'participants':participants
        
        }

    return render(request,'room.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    all_rooms = Room.objects.all().count()
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    context = {
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics,
        'all_rooms':all_rooms
        }
    return render(request,'profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    
    if request.user == None:
        messages.error(request,'you must login')
        return redirect('home')
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)

    if request.user != room.host :
        messages.warning(request,'Your are not allowed here!!')
        return redirect('home')


    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host :
        messages.warning(request,'Your are not allowed here!!')
        return redirect('home')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    room_id = message.room.id
    if request.user != message.user :
        messages.warning(request,'Your are not allowed here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('room',room_id)
    return render(request,'delete.html',{'obj':message})
