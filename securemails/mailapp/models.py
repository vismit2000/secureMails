from django.db import models
from django.contrib.auth.models import User

class msgsData(models.Model):
	key = models.CharField(max_length = 200)
	value = models.CharField(max_length = 1000)

	def __str__(self):
		return self.key

class UserProfileInfo(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	def __str__(self):
  		return self.user.username