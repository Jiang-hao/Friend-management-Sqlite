from django.db import models
# Create your models here.
class Person(models.Model):
	name = models.CharField(max_length=200, unique=True, blank=False, primary_key=True)
	post_message = models.CharField(max_length = 200, default='') # self post
	received_message = models.CharField(max_length = 200, default='') # receive from others

class Friends(models.Model):
	person = models.ForeignKey(Person,on_delete=models.CASCADE)
	
	friends = models.CharField(max_length=200,null=True)

	blocked_friends = models.CharField(max_length=200,null=True)

	follower = models.CharField(max_length=200,null=True)
	 # Friends subscribe this person
	follow = models.CharField(max_length=200,null=True)
 # Friends this person subscribes