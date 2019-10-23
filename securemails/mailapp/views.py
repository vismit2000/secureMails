import json
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from mailapp.models import *
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
	return render(request,'index.html')

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