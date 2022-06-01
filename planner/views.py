from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from datetime import date, timedelta, datetime
import json
from decimal import Decimal

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain, 
	Profile, CompletedAct)
from .forms import (PR_Form, Int_Form, TT_Form, CT_Form, 
	PR_Goal_Form, Int_Goal_Form, SubmissionForm, TT_SubForm, 
	Profile_Form, PaceForm, PlanForm )


# List of all activity models.
ACT_TYPES = [
	PacedRun, 
	Intervals, 
	TimeTrial, 
	CrossTrain
	]
# Activity names and text descriptions for new activity creation menu.
ACT_LIST = [
	{'act_type':ACT_TYPES[0].act_type, 'description': ACT_TYPES[0].description},
	{'act_type':ACT_TYPES[1].act_type, 'description': ACT_TYPES[1].description},
	{'act_type':ACT_TYPES[2].act_type, 'description': ACT_TYPES[2].description},
	{'act_type':ACT_TYPES[3].act_type, 'description': ACT_TYPES[3].description},
	]
# Maps act_types to forms for creating new activity.
ADD_FORMS = {
	ACT_TYPES[0].act_type:PR_Form,
	ACT_TYPES[1].act_type:Int_Form,
	ACT_TYPES[2].act_type:TT_Form,
	ACT_TYPES[3].act_type:CT_Form,
	}
# Forms for setting or editing activity progression / goal values.
GOAL_FORMS = {
	ACT_TYPES[0].act_type:PR_Goal_Form,
	ACT_TYPES[1].act_type:Int_Goal_Form,
	}
# Forms for submitting details of completed activity.	
SUB_FORMS = {
	ACT_TYPES[0].act_type:SubmissionForm,
	ACT_TYPES[1].act_type:SubmissionForm,
	ACT_TYPES[2].act_type:TT_SubForm,
	ACT_TYPES[3].act_type:SubmissionForm,
	}

# Global values for frequently used strings.
dateFormat = "%a %d %b"
rest_string = "Rest Day"

### VIEW FUNCTIONS ###

def home(request):
	"""
	Displays schedule, activities, links for edit/ creation screen.
	"""
	# Declare context dictionary
	context = {}
	# Generate home screen if user logged in, if not prompt to login /register
	if request.user.is_authenticated:
		# Get User profile
		profile = get_profile(request.user)
		# If user has a saved plan, generate schedule.
		if profile.plan:
			schedule_list = get_schedule_list(profile)
			# Check if schedule list has uncompleted activities, if it does 
			# redirect to update view.
			update_list = update_schedule(schedule_list)
			if update_list:
				return render(
					request,
					'planner/update.html',
					context={'update_list':update_list},
					)		
			# Add 'past' attribute to any completed non-rest days.
			for day in schedule_list:
				if day.name != rest_string and day.complete == True:
					day.past = True
			# Add updated schedule to context dict.
			context['schedule_list'] = schedule_list
		
		else:
			# No plan, prompt message to create one
			message = 'Use links below to create activities/ plan'
			context['no_plan_message'] = message
		
		# Get list of user's activities for home screen.
		activities = Activity.objects.filter(owner=request.user)
		context['activities'] = activities
		# Add string representing today's date to context dictionary,
		# used when submitting activity from activity table.
		context['date_iso'] = date.today().isoformat()
	
	return render(request,'planner/home.html', context)


@login_required
def view_history(request):
	"""
	Render page showing table of weekly distance totals.
	"""
	context = {}
	profile = get_profile(request.user)
	if profile.history:
		try:
			history_list = json.loads(profile.history)
			context['history_list'] = history_list
		except:
			context['message'] = 'Error loading history.'
	
	else:
		context['message'] = 'No history to show yet! Please try harder.'
					
	return render(request,'planner/history.html',context)	 


@login_required
def add_new(request,act_type=''):
	"""Display form for creation of new activity types."""
	
	if request.method == "POST":
		# POST request; save new activty from submitted form
		act_type = request.POST.get('act_type')
		form = ADD_FORMS[act_type](data=request.POST)
		if form.is_valid():
			new_activity = form.save(commit=False)
			new_activity.owner = request.user
			new_activity.setvalues()
			new_activity.save()
			# If new activity is progressive, render view for setting goals.
			if new_activity.progressive:
				goal_form = GOAL_FORMS[act_type]
				act_id = new_activity.id
				context = {
					'goal_form':goal_form,
					'act_id':act_id,
					'act_type':act_type
					}
				return render(request,'planner/setgoal.html',context)
		return redirect('planner:home')	
	else:	
		# request from link, provide appropriate form for new activity.
		context = {'ACT_LIST':ACT_LIST}
		# If user clicked on link to create specific activity type,
		# serve form for creation of that.
		if act_type:
			add_form = 	ADD_FORMS[act_type]
			context['add_form'] = add_form
			context['act_type'] = act_type
		return render(request,'planner/addnew.html', context)


@login_required
def mileage(request):
	"""
	Render history of weekly distance.
	"""
	context={}
	profile=get_profile(request.user)
	if profile.mileage_history:
		history_list = json.loads(profile.mileage_history)
		context['history_list']=history_list
	else:
		context['message']='No mileage history yet, complete some activities.'	
	
	return render(request, 'planner/mileage_history.html',context)
	

@login_required
def settings(request):
	"""
	Renders edit user preferences page.

	"""
	profile = get_profile(request.user)
	
	if request.method != 'POST':
		form = Profile_Form(instance=profile)
		paces_form = PaceForm(instance=profile)
		context = {'form':form,'paces_form':paces_form}
		return render(request,'planner/profilesettings.html',context)

	else:
		# POST request, submitted form
		# Save new values	
		form = Profile_Form(instance=profile,data=request.POST)
		if form.is_valid():
			form.save()
		# Check if user has changed plan length setting, if it has been 
		# changed clear plan.
		if form['plan_length'] != profile.plan_length:
			
			profile.schedule_week = 0
			profile.plan = None
			profile.save()
		
		return redirect('planner:home')

@login_required
def savepacesettings(request):
	"""
	Saves submitted pace settings form.
	"""
	if request.method == 'POST':
		profile = get_profile(request.user)		
		pace_form = PaceForm(instance=profile,data=request.POST)
		if pace_form.is_valid():
			pace_form.save()
	
	return redirect('planner:home')

@login_required
def submit(request,act_id,date_iso):
	"""Serve page where user can submit details of completed activity"""
	# Serving form to edit activity.
	if request.method != 'POST':
		# Get activity
		activity = get_act(act_id)
		if not activity or (activity.owner != request.user):
			# Get request has invalid id or id does no bleong to user.
			raise Http404 	
		# Prepopulate form for editing.
		form = SUB_FORMS[activity.my_type]
		context = {
			'activity':activity,
			'form':form,
			'date_iso':date_iso,
			}
		return render(request, 'planner/submit.html',context)

	# Handling submitted form.
	elif request.method == 'POST':
		activity = get_act(request.POST.get('act_id'))
		# Check ownership (shouldn't actually be needed)
		if activity.owner != request.user:
			raise Http404
		model = get_model(activity.my_type)
		# Get instance.
		this_act = model.objects.get(id=act_id)
		# create CompletedAct instance.  
		distance = this_act.distance or 0
		date_done = date.fromisoformat(date_iso)
		completedact = CompletedAct(
			owner=request.user,
			date_done=date_done,
			name = this_act.name,
			distance=distance,
			)
		completedact.save()
		# Update Activity values from Post data
		this_act.update(request.POST,date_done)
		if this_act.progressive and request.POST.get('completed'):
				this_act.progress()
		this_act.setvalues()
		this_act.save()
		# Update user's history
		profile = get_profile(request.user)
		profile = update_history(profile,date_iso,distance,activity.name)
		# If activity has distance value, use it to update mileage.
		if distance:
			profile = update_mileage(profile,date_done,distance)
		# Delete any completed acts that are no longer needed
		clean_completed_acts(request.user,29)
		
		profile.save()				
	return redirect('planner:home')	
		

@login_required
def generate_plan(request):
	"""
	Returns page for setting new plan, saves submitted plan to profile.
	"""
	context ={}
	profile = get_profile(request.user)
	weeks = profile.plan_length
	choices = get_plan_choices(request.user)
	if len(choices) == 1:
		# If length is == 1, list contains only default 'rest day' option.
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
		# Save submitted plan to JSON field on profile.
		profile.plan = json.dumps(plan_dict)
		profile.save()
		return redirect('planner:home')		
	context['form'] = form
	day_list = get_lists(weeks)
	context.update(day_list)
	return render(request,'planner/plan.html',context)


@login_required
def edit(request,act_id=None):
	"""edit the details of an activity"""
	# Get activity instance.
	if not act_id:
		act_id = request.POST.get('act_id')
	activity = get_act(act_id)
	if not activity:
		raise Http404
	# Check ownership.
	if activity.owner != request.user:
		raise Http404			
	
	model = get_model(activity.my_type)
	this_act = model.objects.get(id=act_id)
	# Save Form		
	if request.method == 'POST':
		form = ADD_FORMS[model.act_type](instance=this_act,data=request.POST)
		if form.is_valid():
			form.save()
		this_act.setvalues()
		this_act.save()
		# If progressive, go to setgoals page.
		if this_act.progressive:
			goal_form = GOAL_FORMS[activity.my_type]
			goal_form = goal_form(this_act.goal_prepop())
			context = {
					'goal_form':goal_form,
					'act_id':act_id,
					'act_type':activity.my_type
					}
			return render(request,'planner/setgoal.html',context)		
		# Non-progressive, redirect home.	
		return redirect('planner:home')		
	# Get appropriate form and populate it	
	form = ADD_FORMS[model.act_type](instance=this_act)
	context = {
	'form':form,
	'name':activity.name,
	'act_id':act_id
	}
	return render(request,'planner/edit.html',context)

			
@login_required
def delete(request, act_id=None):
	"""For deleting activities"""
	if not act_id:
		act_id = request.POST.get('act_id')
	activity = get_act(act_id)
	# Check that activity exists and belongs to user.
	if not activity:
		raise Http404
	if activity.owner != request.user:
		raise Http404	
	if request.method != 'POST':
		# From link - serve confirmation form
		context = {'activity':activity}
		return render(request,'planner/delete.html',context)
	if request.method == 'POST':	
		activity.delete()		
		return redirect('planner:home')


@login_required
def restdate(request,date_iso):
	"""
	Creates a rest day with the given date.
	"""
	# Create and save a completed act object with no associated act / distance.
	date_done = date.fromisoformat(date_iso)	
	history = CompletedAct(
		owner=request.user,
		date_done=date_done,
		name=rest_string,
		distance=0.0
		)
	history.save()
	return redirect('planner:home')	


@login_required
def setgoal(request):
	"""Saves values returned from set goal forms when editing or creating"""
	# get activity type
	model = get_model(request.POST.get('act_type'))
	# Get activity being altered.
	act_id = request.POST.get('act_id')
	activity = model.objects.get(id=act_id)
	# Give the values to activity and have it update itself
	activity.setgoals(request.POST)
	activity.setvalues()
	activity.save()	
	return redirect('planner:home')


### HELPERS ###
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
		if not day.complete and day.name != rest_string:
			update_list.append(day)
	if update_list:
		return update_list
	return 0
					

def get_initial_date(t_day):
	"""
	Returns date for most recent Monday(inc today). Returns 0 if
	fed something other than a python date object.
	"""
	try:
		for i in range(7):
			if t_day.strftime("%a") == 'Mon':
				return t_day
			t_day -= timedelta(days=1)	
	except:
		return 0


def get_plan_choices(user):
	"""
	Returns list of 2-tuples to use as choices field on plan creation form.
	The first default item is always a rest day
	"""
	choices = [('REST',rest_string)]
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


def clean_completed_acts(user_id,days):
	"""
	delete any of user's completed_acts older than specified days. Takes
	user_id and number of days to be used as deletion criteria.
	"""
	try:
		user_comp_acts = CompletedAct.objects.filter(owner=user_id)
		for act in user_comp_acts:
			if (date.today() - act.date_done).days >= days:
				act.delete()
		return 1	
	except:
		return 0 	


def update_mileage(profile,date_done,act_distance=0):
	"""
	Add distance value to user's mileage total and return updated profile.
	date_done should be date object, act_distance should be decimal.
	
	"""
	# If activity has no distance value, return unmodified profile to avoid 
	# creating empty rows
	if not act_distance:
		return profile
	# string representing week beginning		
	week_initial_str = get_initial_date(date_done).isoformat()	
	# Load mileage history 
	if profile.mileage_history:
		history = json.loads(profile.mileage_history)
	# Else if no user mileage history yet, create initial entry.
	else:
		history = [
		{
			'date':week_initial_str,
			'distance':'0.0'
			}
		]		
	# If current week still corresponds to history[0], add distance to that 
	# week's total.
	if history[0]['date'] == week_initial_str:
		wtd_distance = Decimal(history[0]['distance'])
		wtd_distance += Decimal(act_distance)
		history[0]['distance'] = f'{wtd_distance}'
	# If current week initial date not in history, create new entry
	else:
		# If (somehow) saving an activity that is in the past and a new
		# week entry has already been made, return unmodified profile.
		# if date older than history[0], ignore
		if (date_done - date.fromisoformat(history[0]['date'])).days < 0: 
			return profile
		# Else if valid, create new entry and add to front of history.

		entry = {
			'date':week_initial_str,
			'distance':str(act_distance)
		}
		history.insert(0,entry)

	# Check history length and trim oldest if necessary
	if len(history) > 50:
		history = history[:49]	
	#Update mileage field on history.
	profile.mileage_history = json.dumps(history)
	return profile		


def update_history(profile,date_iso,distance,name):
	# Create history entry
	if not distance:
		distance = 'n/a'
	historyentry = {
		'date':date_iso,
		'name':name,
		'distance':f'{distance}',
		}
	
	# Check if usr has history, if not create
	if profile.history:
		history = json.loads(profile.history)	
	else: 
		history = []
	# Check history length and trim oldest if necessary
	if len(history) > 50:
		history = history[:49]
	# Add new entry to front of history
	history.insert(0,historyentry)
	profile.history = json.dumps(history)
	return profile	


def get_profile(user):
	"""
	Return profile object for user, if none found initialises one. 
	If not logged in returns 0 .
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


class Day:
	"""
	For constructing schedule list used on home page
	"""
	def __init__(self,day_date,name=rest_string):
		self.date_str = day_date.strftime(dateFormat)
		if day_date == date.today():
			self.date_str = 'Today'
		self.name = name
		self.complete = False
		self.past = False
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
		day = Day(start_date+timedelta(days=i),rest_string)
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