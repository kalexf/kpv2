from django.shortcuts import render, redirect
from datetime import date, timedelta, datetime
import json

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain, 
	Profile,)
from .forms import (PR_Form, Int_Form, TT_Form, CT_Form, PR_Goal_Form, 
	Int_Goal_Form, TT_Goal_Form, SubmissionForm, TT_SubForm, 
	Profile_Form, PlanForm )



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
# Forms for completion, most take standard form.	
SUB_FORMS = {
	ACT_TYPES[0].act_type:SubmissionForm,
	ACT_TYPES[1].act_type:SubmissionForm,
	ACT_TYPES[2].act_type:TT_SubForm,
	ACT_TYPES[3].act_type:SubmissionForm,
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
		
		# Get user's activities for home screen list
		activities = Activity.objects.filter(owner=request.user)
		context['activities'] = activities
		
		# schedule_list should be list of Day objects.
		if profile.plan:
			# 'alt' for testing better version of function, rename
			schedule_list = get_schedule_list(profile)
			context['schedule_list'] = schedule_list
		else:
			# no plan, message to create one
			message = 'Use links below to create activities/ plan'
			context['no_plan_message'] = message


	
	return render(request,'planner/home.html', context)

class Day:
	"""
	For constructing schedule list object used on home page
	"""
	def __init__(self,date,name='Rest Day'):
		self.date_str = date.strftime("%a %d %b")
		if date == date.today():
			self.date_str = 'Today'
		self.name = name

def get_schedule_list(profile):
	"""
	alternative improved version, change docstring
	"""
	# Get date schedule will start from.
	start_date = get_initial_date(date.today())
	# If user has no initial date, create one. Initial date is used to track
	# how many weeks of current plan cycle have passed.	
	if not profile.schedule_init_date:
		profile.schedule_init_date = start_date
		profile.save()
	
	# Load user's activity pattern 'plan'.
	plan = json.loads(profile.plan)
	# Create empty schedule list with correct dates, names all 'rest' 
	sch_list = []
	for i in range(14):
		day = Day(start_date+timedelta(days=i),'Rest Day')
		sch_list.append(day)
	
	# Schedule length in weeks
	weeks = profile.plan_length
	# Plan_days = List of integers, represents which days from user's plan will 
	# be used to create current schedule instance.
	### replace with range when working
	plan_days = [1,2,3,4,5,6,7,1,2,3,4,5,6,7]
	# 1 Week plan will always use this 14-day schedule format
	# Longer plans will vary depending on which week of schedule user is on
	# Schedule week represents which week of their schedule cycle user is on
	schedule_week = 0
	# Replace with range() when working
	a = [1,2,3,4,5,6,7]
	b = [8,9,10,11,12,13,14]
	c = [15,16,17,18,19,20,21]
	d = [22,23,24,25,26,27,28]
	if weeks != 1:
		date_diff = profile.schedule_init_date - get_initial_date(date.today())
		if date_diff.days >= 7:
			schedule_week = date_diff.days / 7
			# If user has completed final week of current schdeule, reset
			# to week 0
			if schedule_week >= weeks:
				schedule_week = 0
				profile.schedule_init_date = get_initial_date(date.today)
				profile.save()

		# Combine number lists to make correct list of plan days, according to
		# plan length anc current week
		if schedule_week == 0:
			plan_days = a + b
		if schedule_week == 1:
			if weeks == 2: 
				plan_days = b + a
			if weeks == 4:
				plan_days = b + c
		if schedule_week == 2:
			plan_days = c + d
		if schedule_week == 3:
			plan_days = d + a		 
		
	# for loop 14, looking up corresponding plan day for each schedule day

	for i in range(14):
		day_value = plan[f'day_{plan_days[i]}']
		if day_value != 'REST':
			activity = get_act(day_value)
			sch_list[i].name = activity.name

	return sch_list
					

def get_initial_date(t_day):
	"""
	Returns date object for most recent Monday(inc today).
	Currently returns initial monday only, not profile.Start_date
	"""
	
	for i in range(7):
		if t_day.strftime("%a") == 'Mon':
			return t_day
		t_day -= timedelta(days=1)	
	return 0

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
		# POST request, submitted form
		# Save new values	
		form = Profile_Form(instance=profile,data=request.POST)
		form.save()
		# Check if user has changed schedule length setting, if it has been 
		# changed clear schedule.
		if form['plan_length'] != profile.plan_length:
			profile.plan = None
			profile.save()

		
		return redirect('planner:home')
		


def generate_schedule(request):
	"""
	Returns Screen where user can build new schedule, saves cubmitted schedule
	to user profile.
	"""
	context ={}
	profile = get_profile(request.user)
	weeks = profile.plan_length
	choices = get_schedule_choices(request.user)
	if len(choices) == 1:
		message = "You need to create some activities before making a schedule"
		context['message'] = message
	try:
		initial_dict = json.loads(profile.plan)
	except:
		initial_dict = {}
	# Generate form with correct number of fields.	
	form = PlanForm(weeks,choices,initial_dict)

	
	if request.method == 'POST':
		#check and save form
		
		form = PlanForm(weeks,choices,request.POST)
		schedule_dict = request.POST.dict()
		schedule_dict.pop('csrfmiddlewaretoken')
		schedule_dict.pop('submit')	
		profile.plan = json.dumps(schedule_dict)
		profile.save()
		

	
	
	
	context['form'] = form
	# get_lists will return dictionary containing n =weeks lists of day names,
	# this is used to determine how many table rows will be created in template	
	day_list = get_lists(weeks)
	context.update(day_list)
	
	return render(request,'planner/schedule.html',context)

def get_schedule_choices(user):
	"""
	Returns list of 2-tuples to use as choices field on schedule creation form.
	The first default item is always a rest day
	"""
	choices = [('REST','Rest Day')]
	activities = Activity.objects.filter(owner=user)
	for act in activities:
		
		choices.append((act.id,act.name))
	return choices	



def get_lists(weeks):
	"""
	Returns dict containing n=weeks lists of weekdays values, 'week_n' keys 
	"""

	days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun',]
	day_dict = {}
	for i in range(weeks):
		day_dict[f'Week_{i+1}'] = days 

	return day_dict	



def testview(request):
	"""for testing"""
	


	return render(request,'planner/testtemplate.html')

def submit(request, act_id):
	"""Serve page where user can submit details of completed activity"""
	# Get activity
	
	if request.method != 'POST':
		
		activity = get_act(act_id)	
		form = SUB_FORMS[activity.my_type]
		context = {'activity':activity,'form':form}
		return render(request, 'planner/submit.html',context)


	elif request.method == 'POST':
		# Gets iD from hidden form field 
		activity = get_act(request.POST.get('act_id'))
		model = get_model(activity.my_type)
		this_act = model.objects.get(id=act_id)
		# Update Activity values from Post data
		this_act.update(request.POST)
		
		if this_act.progressive and request.POST.get('completed'):
				this_act.progress()
		this_act.setvalues()
		this_act.save()


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