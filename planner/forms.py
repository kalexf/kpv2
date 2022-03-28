from django import forms

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain,
	Profile)
from .models import DIFF_CHOICES, DOW_CHOICES, WEEKS_CHOICES




class WeeksForm(forms.Form):
	"""for setting number of weeks in schedule"""
	weeks = forms.ChoiceField(
		choices=[
		(1,'1 Week'),
		(2,'2 Weeks'),
		(4,'4 Weeks'),
		],
		required=True
		)

class ScheduleForm(forms.Form):
	"""
	Dynamic form used for schedule creation page.
	On init needs to be given integer 'weeks' which is used to determine
	number of fields, and list of 2-tuples 'choices', which is used to create
	DD menus for each field. 
	"""

	def __init__(self,weeks,choices,initial_dict=None):
		super(ScheduleForm,self).__init__()
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
		'start_day',
		'mileage_target',
		'mileage_increment'
		]
		labels = {
		'start_day':'Initial Day of week for new schedules',
		'mileage_target':'Weekly distance target (km)',
		'mileage_increment':'Weekly distance increase (km).'
		
		}
		

class PR_Form(forms.ModelForm):
	class Meta:
		model = PacedRun
		fields = [
		'prog_value',
		'pace',
		'minutes',
		'distance',
		'progressive',
			]
		labels = {
		'prog_value':'Track time(minutes) or distance (km)?',
		'pace':'Pace',
		'minutes':'Length(minutes)',
		'distance':'Length(km)',
		'progressive':'Progressive?'
			}
		widgets = {
			'prog_value':forms.RadioSelect,
		}

# Forms for creating new Activity instances- fields vary depending on activity type
class Int_Form(forms.ModelForm):
	class Meta:
		model = Intervals
		fields = [
			'rep_length',
			'rep_number',
			'progressive',
			]
		labels = {
			'rep_length':'Interval length(m)',
			'rep_number':'Repetitions',
			'progressive':'Progressive?'
			}
class TT_Form(forms.ModelForm):
	class Meta:
		model = TimeTrial
		fields = [
			'distance',
			'progressive',
			]
		labels = {
			'distance':'Distance(km)',
			'progressive':'Progressive?'
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

	
class TT_Goal_Form(forms.Form):
	goal_minutes = forms.IntegerField(
		required = False,
		max_value = 720,
		min_value = 0,
		label = 'Goal (minutes)',


		)
	goal_seconds = forms.IntegerField(
		required = False,
		max_value = 59,
		min_value = 0,
		label = 'Goal (seconds)',
		)
	inc_seconds = forms.IntegerField(
		required = False,
		min_value = 1,
		max_value = 60,
		label = 'Increment(seconds)',
		)

	
			