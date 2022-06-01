from django import forms

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain,
	Profile)
from .models import DIFF_CHOICES, WEEKS_CHOICES, PACES

### FORMS ###


class PlanForm(forms.Form):
	"""
	Dynamic form used for training plan creation page.
	On initialisation needs to be given integer 'weeks', 
	and list of 2-tuples 'choices', which is used to create
	select menus for each field. 
	"""

	def __init__(self,weeks,choices,initial_dict=None):
		super(PlanForm,self).__init__()
		for i in range(weeks * 7):
			self.fields[f'day_{i+1}'] = forms.ChoiceField(choices=choices)
		# if initial values have been given, set them
		if initial_dict:
			self.initial.update(initial_dict)

			
class Profile_Form(forms.ModelForm):
	"""
	Form for editing user profile preferences
	"""
	class Meta:
		model = Profile
		fields = [
		
		'plan_length',
		]
		labels = {
		
		'mileage_target':'Weekly distance target (km)',
		'mileage_increment':'Weekly distance increase (km).',
		'plan_length':'How many weeks should one plan cycle be?'
		
		}
		
class PaceForm(forms.ModelForm):
	"""
	For for selecing estimated pace values.
	"""
	class Meta:
		model = Profile
		fields = [
			'pace_0',
			'pace_1',
			'pace_2',
			'pace_3',
			'pace_4',
			]
		labels = {
			'pace_0':PACES[0],
			'pace_1':PACES[1],
			'pace_2':PACES[2],
			'pace_3':PACES[3],
			'pace_4':PACES[4],
		}	
# ADD FORMS -Forms for creating new Activity instances
# - fields vary depending on activity type

class PR_Form(forms.ModelForm):
	class Meta:
		model = PacedRun
		fields = [
		'prog_value',
		'pace',
		'minutes',
		'distance',
		'progressive',
		'customname',
			]
		labels = {
		'prog_value':'Track time(minutes) or distance (km)?',
		'pace':'Pace',
		'minutes':'Length(minutes)',
		'distance':'Length(km)',
		'progressive':'Progressive?',
		'customname':'Use Custom name? Leave blank to use default.',
			}
		widgets = {
			'prog_value':forms.RadioSelect,
		}


class Int_Form(forms.ModelForm):
	class Meta:
		model = Intervals
		fields = [
			'rep_length',
			'rep_number',
			'progressive',
			'customname',
		
			]
		labels = {
			'rep_length':'Interval length(m)',
			'rep_number':'Repetitions',
			'progressive':'Progressive?',
			'customname':'Use Custom name? Leave blank to use default.',
			}
class TT_Form(forms.ModelForm):
	class Meta:
		model = TimeTrial
		fields = [
			'distance',
			'customname',
			]
		labels = {
			'distance':'Distance(km)',
			'customname':'Use Custom name? Leave blank to use default.',
			}			
class CT_Form(forms.ModelForm):
	class Meta:
		model = CrossTrain
		fields = [
			'exercise_type'
			]	
		labels = {
		'exercise_type':'Activity Name'
			}		

class SubmissionForm(forms.Form):
	"""
	Form for entering details of completed non-progressive activities
	"""
	difficulty = forms.ChoiceField(
		choices=DIFF_CHOICES,
		required=True,
		label='How difficult did the activity feel')
	completed = forms.BooleanField(
		label='Activity Targets Met?',
		initial=True,
		required=False)	 
	

# Expanded forms for any activities that need them	
class TT_SubForm(SubmissionForm):
	minutes = forms.IntegerField(
		label='Minutes',
		max_value = 720,
		min_value = 0,
		required = False
		)
	seconds = forms.IntegerField(
		label='Seconds',
		max_value = 59,
		min_value = 0,
		required = False
		)
# Goal forms - for setting progression / goal values of activities

class PR_Goal_Form(forms.Form):
	goal_minutes = forms.IntegerField(
		label='Goal duration(minutes)',
		max_value=720,
		min_value=1,
		required=False
		)
	goal_distance = forms.DecimalField(
		max_value = 100.00,
		min_value = 0.1,
		label = 'Goal distance (km)',
		required = False,
		)
	# Used for both minutes and distance depending on which one is selected / 
	# depending on which progression type is selected 
	increment_value = forms.DecimalField(
		max_value = 100,
		min_value = 0.1,
		label='Progression value TODO',
		required=True,)

class Int_Goal_Form(forms.Form):
	rep_goal = forms.IntegerField(
		label='Goal number of repetitions',
		max_value=100,
		min_value=1
		)
	increment = forms.IntegerField(
		label='Increment - how many reps to add each time',
		max_value=10,
		min_value=1,
		)

	

	
			