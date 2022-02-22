from django.shortcuts import render, redirect
from datetime import date, timedelta, datetime
import json

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain, 
	Profile, Day )
from .forms import (PR_Form, Int_Form, TT_Form, CT_Form, PR_Goal_Form, 
	Int_Goal_Form, TT_Goal_Form, SubmissionForm, Profile_Form)



# List of all activity types
ACT_TYPES = [
	PacedRun, 
	Intervals, 
	TimeTrial, 
	CrossTrain
	]
# Activity names and descriptions for new activity creation menu.
ACT_LIST = [
	{'act_type':ACT_TYPES[0].act_type, 'description': ACT_TYPES[0].description},
	{'act_type':ACT_TYPES[1].act_type, 'description': ACT_TYPES[1].description},
	{'act_type':ACT_TYPES[2].act_type, 'description': ACT_TYPES[2].description},
	{'act_type':ACT_TYPES[3].act_type, 'description': ACT_TYPES[3].description},
	]
# Maps act_types to forms for creating corresponding activity
ADD_FORMS = {
	ACT_TYPES[0].act_type:PR_Form,
	ACT_TYPES[1].act_type:Int_Form,
	ACT_TYPES[2].act_type:TT_Form,
	ACT_TYPES[3].act_type:CT_Form,
	}
# Forms for editing progression / goal values of activities	
GOAL_FORMS = {
	ACT_TYPES[0].act_type:PR_Goal_Form,
	ACT_TYPES[1].act_type:Int_Goal_Form,
	ACT_TYPES[2].act_type:TT_Goal_Form,
	
	}



def home(request):
	"""
	Displays schedule, activities, links for edit/ creation screen.
	"""
	##Testing
	
	context = {}
	# Get a list of the user's activities to display on home screen
	if request.user.is_authenticated:
		
		# Get User profile
		profile = get_profile(request.user)
		#  If no schedule yet, returns 0, schedule section in template empty
		schedule_list = get_schedule(request.user)
		# Get user's activities for home screen list
		activities = Activity.objects.filter(owner=request.user)
	
	
		context['activities'] = activities
		context['profile'] = profile
		context['schedule_list'] = schedule_list

	
	return render(request,'planner/home.html', context)

def settings(request):
	"""
	Returns settings page for profile /schedule.

	"""
	profile = get_profile(request.user)
	
	if request.method != 'POST':

		form = Profile_Form(instance=profile)
		context = {'form':form}

		return render(request,'planner/profilesettings.html',context)

	else:
		##
		form = Profile_Form(instance=profile,data=request.POST)
		form.save()
		return redirect('planner:home')

def next_day_instance(day_integer):
	"""
	Given an integer 0-6 representing day of week, returns the next calendar
	isntance of that day (including today).
	"""
	# Run though next 7 days until correct day found
	try:
		for i in range(0,7):

			day = date.today() + timedelta(days=i)
			if day.weekday() == day_integer:
				# Return python date object for correct day
				return day
	# Will only fail if something other than int 0-6 passed as arg
	except:
		return 0			


def generate_schedule(request):
	"""
	Generate new schedule for user
	"""
	# Get User profile
	profile = get_profile(request.user)
	# Profile copy is used to temporarily store changed values while scheduling
	profilecopy = profile
	# Schedule object is python dictionary which will be covnerted to JSON
	# and stored on user's Profile 
	schedule = {}
	# Get date object corresponding to next calendar date where the day of
	# week corresponds to day of week setting in user profile
	start_date = next_day_instance(profile.start_day)
	# Set dictionary date value to this date (saved this way so it can be more
	# easily serialized to JSON)
	schedule['year'] = start_date.year
	schedule['month'] = start_date.month
	schedule['day'] = start_date.day
	# Number of days in schedule, currently hard-coded to 21
	# length = numbered 'day' objects not total number of keys in dictionary 
	schedule['length'] = 21
	# add numbered items representing sequential days of schedule, set as 
	# rest days initially
	# (this loop could be removed)

	for i in range(0,21):

		schedule[i]='R'
	# Get all of user activities
	activities = Activity.objects.filter(
		owner=request.user)

	day_count = 0
	
	for i in range(0,schedule['length']):
		# Iterating over each numbered day object in sch, initially set to
		# 'r' but assinging integer value representing activity id number
		# when an activity passes tests
		# When i == 7 a full week has been scheduled, values can be reset 
		day_count += 1
		if day_count == 7:
			day_count = 0
			profilecopy.mileage = 0
			if profilecopy.mileage_target:
				profilecopy.mileage_target += profilecopy.mileage_increment
		
	
		# Run through acts array checking if any can pass algo
		for act in activities:
			
			if act.last_done:
				# Calculate if number of days passed since activity was last done
				# is greater than the activity's frequency value.

				days_delta = (start_date + timedelta(days=i)) - act.last_done
				if days_delta.days < act.frequency:
					# Not enough time passed, continue to next act in loop
					continue
			
			if profilecopy.mileage_target:
			# check whether performing the activity would put the user over
			# their mileage target / limit		
				# Will not check unless the activity actually has a distance 
				# value
				if profilecopy.mileage and act.distance:
					mile_delta = profilecopy.mileage_target - profilecopy.mileage
						
					if act.distance > mile_delta:
						# Mileage too large, continue
						continue

			if i > 0:

				if schedule[i-1] != 'R':

					# Will not schedule difficult activity unless previous day
					# was rest
					if act.difficulty == 3:
						continue

					elif act.difficulty == 2:
						# This is not working?
						prev_act = get_act(schedule[i-1])
						if prev_act.difficulty != 1:
			
							continue
			# All tests passed for current act				
			schedule[i] = act.id
			act.last_done = date.today() + timedelta(days=i)
			if act.distance:
				if profilecopy.mileage:

					profilecopy.mileage += act.distance
				else:
					profilecopy.mileage = act.distance

			continue

	schedule_json = json.dumps(schedule)
	profile.schedule = schedule_json
	profile.save()	

	return redirect('planner:home')


def get_schedule(user):
	"""Converts user's saved schedule to list for display on home screen table"""
	# Should probably be refactored to discreet function which will return
	# needed structure / vars
	profile = get_profile(user)
	if profile.schedule:
		# get schedule json and convert to python
		schedule = json.loads(profile.schedule)
		# create list of individual days 
		schedule_list = []
		
		start_day = date(
			year=schedule['year'],
			month=schedule['month'],
			day=schedule['day'],
			)
		length =  schedule['length']
		
		for i in range(length):
			day = Day(date=start_day+timedelta(days=i))
			schedule_list.append(day)

		return schedule_list	
	
	else:
		return 0
	

def testview(request):
	"""for testing"""
	return render(request,'planner/testtemplate.html')

def submit(request, act_id=None):
	"""Serve page where user can submit details of completed activity"""
	# Get activity
	if request.method != 'POST':
		activity = get_act(act_id)
		form = SubmissionForm
		context = {'activity':activity,'form':form}
		return render(request, 'planner/submit.html',context)

	elif request.method == 'POST':
		act_id = request.POST.get('act_id')
		activity = get_act(act_id)
		activity.difficulty = request.POST.get('difficulty')
		activity.last_done = date.today()
		activity.save()

	return redirect('planner:home')	

		# Set act values to form values, save, redirect







def get_profile(user):
	"""
	Return profile object for user, if none found inits one. If not logged in
	returns 0 
	"""
	if user.is_authenticated:
		try:
			profile = Profile.objects.get(owner=user)
		except:
			profile = Profile(owner=user)
			profile.save()	

		return profile
	else:
		return 0	 


def edit(request,act_id=None):
	"""edit the details of an activity"""
	# REFACTORING

	if request.method == 'POST':
		act_id = request.POST.get('act_id')
		activity = get_act(act_id)
		model = get_model(activity.my_type)
		this_act = model.objects.get(id=act_id)
		form = ADD_FORMS[model.act_type](instance=this_act,data=request.POST)
		if form.is_valid():
			form.save()
		this_act.setvalues()
		if this_act.progressive:
			this_act.setgoals(request.POST)	
		this_act.save()
		return redirect('planner:home')	

		#	SAVE CHANGES 

	# Get appropriate form and populate it
	

	activity = get_act(act_id)
	model = get_model(activity.my_type)
	this_act = model.objects.get(id=act_id)
	form = ADD_FORMS[model.act_type](instance=this_act)
	context = {'form':form,'name':activity.name,'act_id':act_id}
	
	# If activity is progressive, get and populate appropriate progression form
	if activity.progressive:
		prog_form = GOAL_FORMS[activity.my_type]

		prog_form = prog_form(this_act.goal_prepop())
		context['prog_form'] = prog_form	
	
	
	return render(request,'planner/edit.html',context)

def delete(request, act_id=None):
	"""For deleting activities"""

	## ! TODO add ownership check / protection
	if request.method != 'POST':
		# From link - serve confirmation form
		activity = get_act(act_id)
		context = {'activity':activity}
		return render(request,'planner/delete.html',context)
	
	if request.method == 'POST':
		
		act_id = int(request.POST.get('act_id'))
		activity = get_act(act_id)
		activity.delete()
		return redirect('planner:home')



	



def setgoal(request):
	"""Saves values returned from set goal forms when editing or creating"""
	
	# get activity type
	model = get_model(request.POST.get('act_type'))
	# Get activity being altered.
	act_id = request.POST.get('act_id')
	activity = model.objects.get(id=act_id)
	
	
	# Give the values to activity and have it update itself
	activity.setgoals(request.POST)
	activity.save()
	# TODO - save


	return redirect('planner:home')

def add_new(request,act_type=''):
	"""display form for creation of new activity types"""
	
	if request.method == "POST":
		# POST request - save new activty from submitted form
		act_type = request.POST.get('act_type')
		form = ADD_FORMS[act_type](data=request.POST)
		
		if form.is_valid():
			new_activity = form.save(commit=False)
			new_activity.owner = request.user
			new_activity.setvalues()
			new_activity.save()


			if new_activity.progressive:

				goal_form = GOAL_FORMS[act_type]

				act_id = new_activity.id

				context = {'goal_form':goal_form,'act_id':act_id,'act_type':act_type}
				return render(request,'planner/setgoal.html',context)



		else:
			# invalid form
			pass

		return redirect('planner:home')	

	else:	
		# request from link, provide appropriate menu / blank form for new activity creation
		context = {'ACT_LIST':ACT_LIST}

		# If user clicked on link to create specific activity type,
		# serve form for creation of that.
		if act_type:
			add_form = 	ADD_FORMS[act_type]
			context['add_form'] = add_form
			context['act_type'] = act_type

		return render(request,'planner/addnew.html', context)

# Helpers

def get_model(act_type):
	"""accepts an activity type and returns the corresponding model"""
	for model in ACT_TYPES:
		if model.act_type == act_type:
			return model
	return 0 		



def get_act(act_id):
	"""accepts an id number and returns the associated act, returns 0 if
	activity does not exist"""
	try:
		return Activity.objects.get(id=act_id)
	except:
		return 0	