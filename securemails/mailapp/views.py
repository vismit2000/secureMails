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
def index(request):
	if ((request.user is not None) and (request.user.is_authenticated)):
		print('yayyy')
		print(request.user)
		keysDict = getKeysData(request)
		keysDict['usermail'] = UserProfileInfo.objects.get(user = request.user).user.email
		return render(request,'home.html', keysDict)
	return render(request,'login.html')

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
	keysDict = getKeysData(request)
	keysDict['usermail'] = UserProfileInfo.objects.get(user = request.user).user.email
	return render(request,'home.html',keysDict)

# @login_required
def getKeysData(request):
	users = UserProfileInfo.objects.all()
	usersList = [] 
	for i in range(len(users)):
		userobj = {}
		userobj['name'] = users[i].user.username
		userobj['email'] = users[i].user.email
		userobj['pubkey'] = users[i].userPubKey
		usersList.append(userobj)
	print(usersList)

	user = UserProfileInfo.objects.get(user = request.user)
	pubKey = user.userPubKey
	keyExists = False
	if(pubKey == 'xxxxxxxxxx'):
		keyExists = False
	else:
		keyExists = True

	keysDict = {'usersList':json.dumps(usersList),'keyExists':keyExists, 'key':pubKey }
	return keysDict

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
def savekey(request):
	print('save keys')
	res = {}
	if request.method == 'POST':
		reqObj = json.loads( request.body.decode('utf-8') )
		msgJsonData = reqObj
		key = msgJsonData['key']
		user = UserProfileInfo.objects.get(user = request.user)
		user.userPubKey = key
		user.save()
		res['message'] = 'Data saved Successfully'
		res['error'] = 'No Error'
	else:
		res['error'] = 'Not recieved a post request'
	print(res)
	return JsonResponse(res)

@csrf_protect
def saveSessionKey(request):
	print('save session key')
	res = {}
	if request.method == 'POST':
		reqObj = json.loads( request.body.decode('utf-8') )
		msgJsonData = reqObj
		
		userA = msgJsonData['userA']
		userB = msgJsonData['userB']
		keyEncA = msgJsonData['keyEncA']
		keyEncB = msgJsonData['keyEncB']
		# user = request.user
		obj, created = SessionKeysEnc.objects.get_or_create(userA = userA, userB = userB, keyEncA = keyEncA, keyEncB = keyEncB)
		if(created == True):
			res['message'] = 'Data saved Successfully'
			res['error'] = 'No Error'
		else:
			res['error'] = 'Error in saving sessionkeys'	
	else:
		res['error'] = 'Not recieved a post request'
	print(res)
	return JsonResponse(res)

@csrf_protect
def getSessionKey(request):
	print('get session key')
	res = {}
	if request.method == 'POST':
		reqObj = json.loads( request.body.decode('utf-8') )
		msgJsonData = reqObj
		
		userA = msgJsonData['userA']
		userB = msgJsonData['userB']
		encKey = ''
		# user = request.user
		try:
			sessionKeyObj = SessionKeysEnc.objects.get(userA = userA, userB = userB)
			if userA == request.user.email:
				enckey = sessionKeyObj.keyEncA
			else:
				encKey = sessionKeyObj.keyEncB
		except SessionKeysEnc.DoesNotExist:
			try:
				sessionKeyObj = SessionKeysEnc.objects.get(userA = userB, userB = userA)
				if userA == request.user.email:
					enckey = sessionKeyObj.keyEncA
				else:
					encKey = sessionKeyObj.keyEncB
			except SessionKeysEnc.DoesNotExist:
				print('Key dne')
		
		
			res['sessionKey'] = encKey
			res['message'] = 'Data saved Successfully'
			res['error'] = 'No Error'
		else:
			res['error'] = 'Error in saving sessionkeys'	
	else:
		res['error'] = 'Not recieved a post request'
	print(res)
	return JsonResponse(res)

@csrf_protect
def getparams(request):
	print('hi')
	params = {}
	params['ivsaltsender'] = request.GET.get('ivsaltsender')
	
	saltindex = params['ivsaltsender'].index('|@@@@@|')
	mailIndex = params['ivsaltsender'].index('|!!!!!|')
	
	iv = params['ivsaltsender'][0:saltindex]
	salt = params['ivsaltsender'][saltindex+7:mailIndex]
	
	sendrMail = params['ivsaltsender'][mailIndex+7:]
	
	params['iv'] = iv
	params['salt'] = salt
	# params['sendr'] = sendrMail

	msgObject = msgsData.objects.get(key = iv+'|@|'+salt)
	encKey = ''
	try:
		sessionKeyObj = SessionKeysEnc.objects.get(userA = sendrMail, userB = request.user.email)
		enckey = sessionKeyObj.keyEncB
	except SessionKeysEnc.DoesNotExist:
		try:
			sessionKeyObj = SessionKeysEnc.objects.get(userA = request.user.email, userB = sendrMail)
			enckey = sessionKeyObj.keyEncA
		except SessionKeysEnc.DoesNotExist:
			print('Key dne')

	params['msgObj'] = json.loads(msgObject.value)
	
	print(type(msgObject))
	print(params)
	
	keysDict = getKeysData(request)
	keysDict['usermail'] = UserProfileInfo.objects.get(user = request.user).user.email
	keysDict['msgObj'] = params['msgObj']
	keysDict['symmKeyEnc'] = encKey
	keysDict['sender'] = sendrMail
	
	return render(request,'home.html', keysDict)
	