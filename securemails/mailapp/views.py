import json
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from mailapp.models import *
from django.urls import reverse

def index(request):
	return render(request,'index.html')

def savedata(request):
	print('hi')
	res = {}
	if request.method == 'POST':
		reqObj = json.loads( request.body.decode('utf-8') )
		msgJsonData = json.loads( reqObj['body'] )
		msgsEntry = msgsData(key = msgJsonData['key'],value= json.dumps(msgJsonData['value']))
		msgsEntry.save()
		res['message'] = 'Data saved Successfully'
		res['error'] = 'No Error'
	else:
		res['error'] = 'Not recieved a post request'
	print(res)
	return JsonResponse(res)