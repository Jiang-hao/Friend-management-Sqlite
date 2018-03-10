from django.shortcuts import render
import json
from django.http import HttpResponse
# Create your views here.
from rest_framework import generics
from .serializers import *
from .models import *
from django.core import serializers
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
import datetime
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.shortcuts import render
import re

class CreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()

def index(request):
	persons = Person.objects.all()
	context = {'allPersons': persons}
	if request.is_ajax():
		t = 'partial.html'
	else:
		t = 'index.html'
	#html = t.render(context)
	return render(request,t,context)


def listAll(request):
	res={}
	persons = Person.objects.all()
	context = {'allPersons': persons}
	return render(request,'templates/index.html',context)


@csrf_exempt
def connect(request):
	data = request.POST.getlist('friends[]')
	requestor = data[0]
	target = data[1]
	res={}
	try:
	 	if bool(Person.objects.filter(name=requestor)):
	 		#Record exists
	 		requestor_obj = Person.objects.get(name=requestor)
	 	else:
	 		#No records
	 		Person.objects.create(name=requestor,post_message='',received_message='')
	 		requestor_obj = Person.objects.get(name=requestor)
	 		Friends.objects.create(person=requestor_obj,friends='', blocked_friends='',follower='',follow='' )

	 	if bool(Person.objects.filter(name=target)):
	 		#Record exists
	 		target_obj = Person.objects.get(name=target)
	 	else:
	 		#No records
	 		Person.objects.create(name=target,post_message='',received_message='')
	 		target_obj = Person.objects.get(name=target)
	 		Friends.objects.create(person=target_obj,friends='', blocked_friends='',follower='',follow='' )
	 	
	 	try:
	 		#Record exists
	 		requestor_friends = Friends.objects.get(person=requestor_obj)
	 		#Check if target blocked requestor
	 		target_friends = Friends.objects.get(person=target_obj)
	 		if (requestor in target_friends.blocked_friends):
	 			res['success'] = False
		 		res['reason'] = target + " blocked "+requestor +". Cannot connect"	
		 	elif (target in requestor_friends.blocked_friends):
		 		res['success'] = False
		 		res['reason'] = requestor + " blocked "+target +". Cannot connect"
		 	else:
		 		#Not blocked
		 		if target not in requestor_friends.friends:
		 			new_friends_str = requestor_friends.friends + ' ' + target
			 		requestor_friends.friends = new_friends_str
			 		requestor_friends.save()
			 		res['success'] = True
			 	else:
			 		res['success'] = False
			 		res['reason'] = target + " is already a friend of "+requestor
		 		
		 		if requestor not in target_friends.friends:
			 		new_friends_str = target_friends.friends + ' ' + requestor
			 		target_friends.friends = new_friends_str
			 		target_friends.save()
			 		res['success'] = True
			 	else:
			 		res['success'] = False
			 		res['reason'] = target + " is already a friend of "+requestor
	 	except Exception as e:
	 		res['success'] = False
	 		res['reason'] = "Error occured: "+ str(e) 
 	# try:
 	# 	requestor_friends = Friends.objects.get(person=requestor_obj)
 	# 	requestor_friends.friends.append(target)
 	# 	res['success'] = True
 	# except:
 	# 	res['success'] = False
 	# res['success'] = requestor_obj.name
	except Exception as e:
 		res['success'] = False
 		res['reason'] = "Error occured: "+ str(e)	
	return HttpResponse(json.dumps(res))

@csrf_exempt
def retrieve(request):
	res={}
	email = request.POST.get('email')
	try:
		the_person = Person.objects.get(name=email)

	except:
		res['success'] = False
		res['reason'] = email + " is not in Person database"
		return HttpResponse(json.dumps(res))
	try:
		friend_list = Friends.objects.get(person=the_person).friends.split(' ')
		friend_list = list(filter(None,friend_list))
	except:
		res['success'] = False
		res['reason'] = email + " is not in Friends database"
		return HttpResponse(json.dumps(res))

	
	res['success'] = True
	res['friends'] = friend_list
	res['count'] = len(friend_list)

	return HttpResponse(json.dumps(res))


@csrf_exempt
def common(request):
	data = request.POST.getlist('friends[]')
	requestor = data[0]
	target = data[1]
	res={}
	try:
		requestor_person = Person.objects.get(name=requestor)

	except:
		Person.objects.create(name=requestor,post_message='',received_message='')
		requestor_person = Person.objects.get(name=requestor)
		Friends.objects.create(person=requestor_person,friends='', blocked_friends='',follower='',follow='' )

	try:
		target_person = Person.objects.get(name=target)

	except:
		Person.objects.create(name=target,post_message='',received_message='')
		target_person = Person.objects.get(name=target)
		Friends.objects.create(person=target_person,friends='', blocked_friends='',follower='',follow='' )

	try:
		requestor_friend_list = Friends.objects.get(person=requestor_person).friends.split(' ')
		requestor_friend_list = list(filter(None,requestor_friend_list))
	except Exception as e:
		res['success'] = False
		res['reason'] = "error: " + str(e)
		return HttpResponse(json.dumps(res))
	try:
		target_friend_list = Friends.objects.get(person=target_person).friends.split(' ')
		target_friend_list = list(filter(None,target_friend_list))
	except Exception as e:
		res['success'] = False
		res['reason'] = "error: " + str(e)
		return HttpResponse(json.dumps(res))
	
	commont_friends= list(set(requestor_friend_list).intersection(target_friend_list))	


	res['success'] = True
	res['friends'] = commont_friends
	res['count'] = len(commont_friends)

	return HttpResponse(json.dumps(res))

@csrf_exempt
def follow(request):
	
	res={}
	requestor = request.POST.get('requestor')
	target = request.POST.get('target')
	try:
		requestor_person = Person.objects.get(name=requestor)

	except:
		#Not in Person db. Create one for requestor
		Person.objects.create(name=requestor,post_message='',received_message='')
		requestor_person = Person.objects.get(name=requestor)
		Friends.objects.create(person=requestor_person,friends='',blocked_friends='',follower='',follow='')
	

	try:
		target_person = Person.objects.get(name=target)

	except:
		#Not in Person db. Create one for requestor
		Person.objects.create(name=target,post_message='',received_message='')
		target_person = Person.objects.get(name=target)
		Friends.objects.create(person=target_person,friends='',blocked_friends='',follower='',follow='')

	
	try:
		requestor_follow = Friends.objects.get(person=requestor_person)
		new_follow_str = requestor_follow.follow + ' ' + target
		requestor_follow.follow = new_follow_str
		requestor_follow.save()

	except:
		res['success'] = False
		res['reason'] = requestor + " cannot follow "+ target
		return HttpResponse(json.dumps(res))
	

	try:
		target_follower = Friends.objects.get(person=target_person)
		new_follower_str = target_follower.follower + ' ' + requestor
		target_follower.follower = new_follower_str
		target_follower.save()
	except:
		res['success'] = False
		res['reason'] = target + " cannot add " +requestor+" as follower"
		return HttpResponse(json.dumps(res))


	
	res['success'] = True

	return HttpResponse(json.dumps(res))



@csrf_exempt
def block(request):
	
	res={}
	requestor = request.POST.get('requestor')
	target = request.POST.get('target')
	try:
		requestor_person = Person.objects.get(name=requestor)

	except:
		#Not in Person db. Create one for requestor
		Person.objects.create(name=requestor,post_message='',received_message='')
		requestor_person = Person.objects.get(name=requestor)
		Friends.objects.create(person=requestor_person,friends='',blocked_friends='',follower='',follow='')
	

	try:
		target_person = Person.objects.get(name=target)

	except:
		#Not in Person db. Create one for requestor
		Person.objects.create(name=target,post_message='',received_message='')
		target_person = Person.objects.get(name=target)
		Friends.objects.create(person=target_person,friends='',blocked_friends='',follower='',follow='')

	
	try:
		requestor_blocks = Friends.objects.get(person=requestor_person)
		new_block_str = requestor_blocks.blocked_friends + ' ' + target 
		requestor_blocks.blocked_friends = new_block_str
		requestor_blocks.save()

	except:
		res['success'] = False
		res['reason'] = requestor + " cannot block "+ target
		return HttpResponse(json.dumps(res))
	
	res['success'] = True

	return HttpResponse(json.dumps(res))




@csrf_exempt
def message(request):
	
	res={}
	receiver=[]
	sender = request.POST.get('sender')
	text = request.POST.get('text')
	try:
		sender_person = Person.objects.get(name=sender)

	except:
		#Not in Person db. Create one for requestor
		Person.objects.create(name=sender,post_message='',received_message='')
		sender_person = Person.objects.get(name=sender)
		Friends.objects.create(person=sender_person,friends='',blocked_friends='',follower='',follow='')
	
	try:
		sender_friends = Friends.objects.get(person=sender_person)

		sender_friends_list = sender_friends.friends.split(' ')
		sender_friends_list = list(filter(None,sender_friends_list))
		
		sender_follower_list = sender_friends.follower.split(' ')
		sender_follower_list = list(filter(None,sender_follower_list))

		#Condition 1: Friends of sender, and didnt block sender
		for item in sender_friends_list:
			item_person = Person.objects.get(name=item)
			item_friends = Friends.objects.get(person=item_person)
			if sender not in item_friends.blocked_friends:
				if item not in receiver:
					receiver.append(item)

		#Condition 2: Followers of sender, and didnt block sender
		for item in sender_follower_list:
			item_person = Person.objects.get(name=item)
			item_friends = Friends.objects.get(person=item_person)
			if sender not in item_friends.blocked_friends:
				if item not in receiver:
					receiver.append(item)

		#Condition 3: Mentions
		mentions_in_text = re.findall(r'[\w\.-]+@[\w\.-]+', text)
		for item in mentions_in_text:
			try:
				item_person = Person.objects.get(name=item)
			except:
				Person.objects.create(name=item,post_message='',received_message='')
				item_person = Person.objects.get(name=item)
				Friends.objects.create(person=item_person,friends='',blocked_friends='',follower='',follow='')
			
			item_friends = Friends.objects.get(person=item_person)
			if sender not in item_friends.blocked_friends:
				if item not in receiver:
					receiver.append(item)
		
		res['success'] = True
		res['recipients'] = receiver
	except Exception as e:
		res['success'] = False
		res['reason'] = 'Error: '+str(e)

	return HttpResponse(json.dumps(res))