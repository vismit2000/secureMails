from django.db import models
from django.contrib.auth.models import User

class msgsData(models.Model):
	key = models.CharField(max_length = 200)
	value = models.TextField(max_length = 1000)

	def __str__(self):
		return self.key

class UserProfileInfo(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	userPubKey = models.CharField(max_length = 1000, default = 'xxxxxxxxxx')
	# userPrivKey = models.CharField(max_length = 1000, default = 'xxxxxxxxxx')
	def __str__(self):
  		return self.user.username

class SessionKeysEnc(models.Model):
	userA = models.CharField(max_length = 100)
	userB = models.CharField(max_length = 100)
	keyEncA = models.TextField(default = 'xxxxxxxxxx')
	keyEncB = models.TextField(default = 'xxxxxxxxxx')
	def __str__(self):
  		return self.userA+' and '+self.userB