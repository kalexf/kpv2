from django.shortcuts import render, redirect
from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain )
from .forms import PR_Form, Int_Form, TT_Form, CT_Form
from .forms import PR_Goal_Form, Int_Goal_Form, TT_Goal_Form, SubmissionForm
from datetime import date
 #timedelta



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



		# From confirmation form - delete

	# Render confirmation page

	# Delete

	# Redirect to Home page

def home(request):
	"""home screen"""
	# Get a list of the user's activities to display on home screen
	activities = Activity.objects.filter(owner=request.user)
	
	context = {'activities':activities}
	return render(request,'planner/home.html', context)


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