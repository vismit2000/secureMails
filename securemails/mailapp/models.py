from django.db import models

class msgsData(models.Model):
	key = models.CharField(max_length = 200)
	value = models.CharField(max_length = 1000)

	def __str__(self):
		return self.key