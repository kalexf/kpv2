from django.shortcuts import render, redirect
from datetime import date, timedelta, datetime
import json
from decimal import Decimal

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain, 
	Profile, CompletedAct)
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
# Used with date.strptime, strftime.
dateFormat = "%a %d %b"



def home(request):
	"""
	Displays schedule, activities, links for edit/ creation screen.
	"""

	
	# Declare context dictionary
	context = {}
	# Generate home screen if user is logged in, if not just prompt to
	# login /register
	if request.user.is_authenticated:
		# Get User profile
		profile = get_profile(request.user)
		# If user has a saved plan, build schedule schedule.
		if profile.plan:
			schedule_list = get_schedule_list(profile)
			# Check if schedule list has uncompleted parts, if it does redirect 
			# to confirmation screen to update
			update_list = update_schedule(schedule_list)
			
			if update_list:
				return render(
					request,
					'planner/update.html',
					context={'update_list':update_list},
					)
			
			
			

			context['schedule_list'] = schedule_list
		
		# Get user's activities for home screen list
		else:
			# No plan, prompt message to create one
			message = 'Use links below to create activities/ plan'
			context['no_plan_message'] = message
		# Update distances
		wtd_distance = update_distance(profile)
		activities = Activity.objects.filter(owner=request.user)
		context['activities'] = activities
		context['date_iso'] = date.today().isoformat()
		context['wtd_distance'] = wtd_distance

	
	return render(request,'planner/home.html', context)

def update_distance(profile):
	"""
	update distance totals and delete any completed acts which are no longer needed.
	Return week to date total distance or 0.
	"""
	# Declare decimal for week-to-date distance value.
	wtd_distance = 0.0	
	# Check profile has current week value
	if not profile.current_week_initial:
		profile.current_week_initial = get_initial_date(date.today())
		profile.save()
	# Check / update history for completedacts older than 1 week.
	# Get Queryset of all user's completed activity history.	
	completed_acts = CompletedAct.objects.filter(owner=profile.owner)
	if completed_acts.exists():
		start_date = profile.current_week_initial
		end_date = start_date + timedelta(days=6)
		# If more than a week has passsed since initial date, archive mileage
		# and delete old CompletedActs
		if end_date < date.today():
			completed_acts.filter(date_done__range=[start_date,end_date])
			# Calculate mileage of compacts in this range
			distance = get_distance(completed_acts)
			history = json.loads(profile.history)
			# Create new entry
			new_entry = {
				'dates':f'{start_date.iso_format()} to {end_date.iso_format()}',
				'distance':distance
				}
			if history:
				# Add entry to list and save.
				history.append(new_entry)
				profile.history = json.dumps(new_entry)
			else:
				#No history, add first entry and save
				history = [new_entry]
				profile.history = json.dumps(history)
				profile.save() 	
			# Delete archived comp acts
			completed_acts.delete()
			new_week_initial = profile.current_week_initial + timedelta(days=7)
			profile.current_week_initial = new_week_initial
			profile.save()
		completed_acts = CompletedAct.objects.filter(owner=profile.owner)
		if completed_acts.exists():
			wtd_distance = get_distance(completed_acts)
			if wtd_distance:
				return wtd_distance

	
	else:
		# No completed_acts - nothing to update, no mileage, return 0.0
		return wtd_distance		

	return 0		

def get_distance(q_set):
	"""
	returns the total distance value of acts in a queryset (or other iterable)
	as a decimal, or returns 0.0 if none. 
	"""
	distance_value = Decimal(0.0)
	for act in q_set:
		if act.distance:
			distance_value += act.distance
	
	return distance_value		


def save_mileage(start_date,end_date,distance,profile):
	"""
	Saves mileage values and date strings to json field on profile, which
	is used for viewing mileage history.

	"""
	# INCLUDING THIS IN UPDATE_DISTANCE FOR NOW

	return 0

def update_schedule(schedule_list):
	"""
	returns days that need updating, or 0 if there are none
	"""
	update_list = []
	for day in schedule_list:
		# iterate over schedule days up to today.
		if day.date_str == 'Today':
			break
		# Add any that are incomplete And not rest days to list.
		if not day.complete and day.name != 'Rest Day':
			update_list.append(day)
	if update_list:
		return update_list
	return 0

class Day:
	"""
	For constructing schedule list used on home page
	"""
	def __init__(self,day_date,name='Rest Day'):
		self.date_str = day_date.strftime(dateFormat)
		if day_date == date.today():
			self.date_str = 'Today'
		self.name = name
		self.complete = False
		self.act_id = 0
		# Added to fix a bug where schedule spanned new year
		self.date_iso = day_date.isoformat()

def get_schedule_list(profile,replace=True):
	"""
	Creates a list of 14 'day' objects, based on user's plan. Used on home
	screen to display two week schedule.
	if replace=True, will check schedule against completed activities, if any
	dates overlap the scheduled activity will be replaced with the completed
	activity.
	"""

	# Check how many days have passed since the initial date of current schedule
	if not profile.schedule_init_date:
		profile.schedule_init_date = get_initial_date(date.today())

	date_diff = date.today() - profile.schedule_init_date
	if date_diff.days >= 7:
		# At least one week has passed, reset schedule initial date.
		profile.schedule_week += 1
		profile.schedule_init_date = get_initial_date(date.today())
		if profile.schedule_week >= profile.plan_length:
			# Passed end of plan, reset to week 0

			profile.schedule_week = 0 
		profile.save()

	# Load user's activity pattern 'plan'.
	plan = json.loads(profile.plan)
	# Create empty schedule list with correct dates, names all 'rest' 
	sch_list = []
	start_date = profile.schedule_init_date
	for i in range(14):
		day = Day(start_date+timedelta(days=i),'Rest Day')
		sch_list.append(day)
	
	# Plan_days = List of integers, represents which days from user's plan will 
	# be used to create current schedule instance.
	plan_days = [1,2,3,4,5,6,7,1,2,3,4,5,6,7]
	# 1 Week plan will always use this 14-day schedule format,longer plans 
	# will vary depending on which week of schedule user is on.
	
	a = [1,2,3,4,5,6,7]
	b = [8,9,10,11,12,13,14]
	c = [15,16,17,18,19,20,21]
	d = [22,23,24,25,26,27,28]

	if profile.plan_length != 1:
		week = profile.schedule_week
		# Combine number lists to make correct list of plan days, according to
		# plan length anc current week
		if week == 0:
			plan_days = a + b
		if week == 1:
			if profile.plan_length == 2: 
				plan_days = b + a
			if profile.plan_length == 4:
				plan_days = b + c
		if week == 2:
			plan_days = c + d
		if week == 3:
			plan_days = d + a		 
		
	# Create schedule list object, copying plan activities to correct position
	# in schedule.

	for i in range(14):
		day_value = plan[f'day_{plan_days[i]}']
		if day_value != 'REST':
			activity = get_act(day_value)
			if activity:
				sch_list[i].name = activity.name
				sch_list[i].act_id = day_value
	
	if replace == True:
		# Look up user's completed activities
		past_acts = CompletedAct.objects.filter(owner=profile.owner)
		
		for day in sch_list:
			for past_act in past_acts:
				if day.date_str == past_act.date_done.strftime(dateFormat):
					day.name = past_act.name
					day.complete = True
			if day.date_str == 'Today':
				for past_act in past_acts:
					if past_act.date_done == date.today():
						day.name = past_act.name
						day.complete = True		

	return sch_list
					

def get_initial_date(t_day):
	"""
	Returns date object for most recent Monday(inc today). Will cause error if
	fed something other than date object.
	"""
	for i in range(7):
		if t_day.strftime("%a") == 'Mon':
			return t_day
		t_day -= timedelta(days=1)	
	return 0

def settings(request):
	"""
	Renders edit user preferences page.

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
		# Check if user has changed plan length setting, if it has been 
		# changed clear plan.
		if form['plan_length'] != profile.plan_length:
			
			profile.schedule_week = 0
			profile.plan = None
			profile.save()

		
		return redirect('planner:home')
		


def generate_plan(request):
	"""
	Returns Screen where user can build new plan, saves submitted plan
	to user profile.
	"""
	context ={}
	profile = get_profile(request.user)
	weeks = profile.plan_length
	choices = get_plan_choices(request.user)
	if len(choices) == 1:
		message = "You need to create some activities before making a plan"
		context['message'] = message
	# initial dictionary is used to pre-populate the plan form with user's 
	# current plan, if they have one.
	try:
		initial_dict = json.loads(profile.plan)
	except:
		initial_dict = {}
	# Generate custom form with correct number of fields, choices.	
	form = PlanForm(weeks,choices,initial_dict)

	
	if request.method == 'POST':
		#check and save form
		
		form = PlanForm(weeks,choices,request.POST)
		plan_dict = request.POST.dict()
		# Remove unnecessary fields.
		plan_dict.pop('csrfmiddlewaretoken')
		plan_dict.pop('submit')	
		# Save submitted plan to JSON field.
		profile.plan = json.dumps(plan_dict)
		profile.save()
		return redirect('planner:home')

	
	
	
	context['form'] = form
	day_list = get_lists(weeks)
	context.update(day_list)
	
	return render(request,'planner/plan.html',context)

def get_plan_choices(user):
	"""
	Returns list of 2-tuples to use as choices field on plan creation form.
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

def submit(request,act_id,date_iso):
	"""Serve page where user can submit details of completed activity"""
	# Get activity
	
	if request.method != 'POST':
		
		activity = get_act(act_id)	
		form = SUB_FORMS[activity.my_type]
		context = {
		'activity':activity,
		'form':form,
		'date_iso':date_iso,
		}
		return render(request, 'planner/submit.html',context)


	elif request.method == 'POST':
		# Gets iD from hidden form field 
		activity = get_act(request.POST.get('act_id'))
		model = get_model(activity.my_type)
		this_act = model.objects.get(id=act_id)
		# create CompletedAct entry. Created / saved before progression to get
		# accurate values for activity name. 
		distance = this_act.distance or 0
		date_done = date.fromisoformat(date_iso)


		history = CompletedAct(
			owner=request.user,
			date_done=date_done,
			name = this_act.name,
			distance=distance,
			)
		history.save()

		# Update Activity values from Post data
		this_act.update(request.POST)
		
		if this_act.progressive and request.POST.get('completed'):
				this_act.progress()
		this_act.setvalues()
		this_act.save()

	return redirect('planner:home')	

def restdate(request,date_iso):
	"""
	Creates a rest day with the given date.
	"""
	# Create and save a completed act object with no associated act / distance.
	date_done = date.fromisoformat(date_iso)

	
	history = CompletedAct(
		owner=request.user,
		date_done=date_done,
		name='Rest Day',
		distance=0.0
		)
	history.save()
	return redirect('planner:home')	

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

