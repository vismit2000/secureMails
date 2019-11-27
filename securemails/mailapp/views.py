import json
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from mailapp.models import *
from mailapp.forms import UserForm,UserProfileInfoForm
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

'''
*if the user is logged in already, then home page is rendered
*else directed to login page
'''
@login_required
def index(request):
	if request.user.is_authenticated:
		return render(request,'home.html')
	return render(request,'index.html')

def special(request):
	return HttpResponse("You are logged in !")

'''
directs to login page, authentication is nullified
'''
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/mailapp/user_login/')

'''
Called for registering
*receives request from frontend when user tries to register
*request has the information to be registered
*if type of request=POST, saves the user details in the SQLITE3 database
*else registration page is rendered again
*
'''
def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		# print(user_form)
		profile_form = UserProfileInfoForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			# our_user = UserProfileInfo(user = user_form.save(),indicesList = "'NDVI':'(nir-r)/(nir+r)'")
			# print(our_user)
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			# our_user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			profile.save()
			registered = True
		else:
			print(user_form.errors,profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileInfoForm()
	return render(request,'registration.html',
						  {'user_form':user_form,
						   'profile_form':profile_form,
						   'registered':registered})
'''
Called for loggin in
*request has the username and password given in by the user
This function-
*after receiving request(POST) for login, authenticates the requesting user's 
password and username
*if successful, directed to home page
*login page rendered again in case the request is not of the type POST
'''
def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		t_res={}
		t_res['username']=username
		t_res['password']=password
		# print(t_res)
		#need to return this response
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth_login(request,user)
				#return HttpResponseRedirect(reverse('index'))
				#go to the map interface after this
				return redirect('/mailapp/home/')
			else:
				return HttpResponse("Your account was inactive.")
		else:
			print("Someone tried to login and failed.")
			print("They used username: {} and password: {}".format(username,password))
			return HttpResponse("Invalid login details given")
	else:
		return render(request, 'login.html', {})

'''
stores the id of the user logging in and renders home page
'''	
@login_required
def home(request):
	id = request.user.id
	# print(request.user)
	user = UserProfileInfo.objects.get(user = request.user)
	print('hi')
	print(user)
	users = UserProfileInfo.objects.all()
	usersList = [] 
	for i in range(len(users)):
		userobj = {}
		userobj['name'] = users[i].username
		userobj['email'] = users[i].email
		usersList.append(userobj)
	print(usersList)
	return render(request,'home.html',{'usersList':usersList})

def login(request):
	return render(request,'login.html')

@csrf_protect
def savedata(request):
	print('hi')
	res = {}
	if request.method == 'POST':
		reqObj = json.loads( request.body.decode('utf-8') )
		msgJsonData = reqObj
		msgsEntry = msgsData(key = msgJsonData['key'],value= json.dumps(msgJsonData['value']))
		msgsEntry.save()
		res['message'] = 'Data saved Successfully'
		res['error'] = 'No Error'
	else:
		res['error'] = 'Not recieved a post request'
	print(res)
	return JsonResponse(res)

@csrf_protect
def getparams(request):
	params = {}
	params['ivsalt'] = request.GET.get('ivsalt')
	saltindex = params['ivsalt'].index('|@@@@@|')
	iv = params['ivsalt'][0:saltindex]
	salt = params['ivsalt'][saltindex+7:]
	params['iv'] = iv
	params['salt'] = salt
	msgObject = msgsData.objects.get(key = iv+'|@|'+salt)
	params['msgObj'] = json.loads(msgObject.value)
	print(type(msgObject))
	print(params)
	return render(request,'index.html', {'msgObj': params['msgObj']})