from django import forms

from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain,
	Profile)
from .models import DIFF_CHOICES, DOW_CHOICES

# Forms for creating new Activity instances- fields vary depending on activity type


class Profile_Form(forms.ModelForm):
	"""
	Form for editing user profile preferences
	"""
	class Meta:
		model = Profile
		fields = [
		'start_day'
		]
		labels = {
		'start_day':'Initial Day of week for new schedules'
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
	"""Form for entering details of completed activities"""

	difficulty = forms.ChoiceField(
		choices=DIFF_CHOICES,
		required=True,
		label='How difficult did the activity feel') 
	# Choices / radio fields for recording difficulty and
	# whether activity fully done



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
		min_value = 0,
		label = 'Goal distance (km)',
		required = False,
		)
	# Used for both minutes and distance depending on which one is selected / 
	# depending on which progression type is selected 
	increment_value = forms.IntegerField(
		max_value = 100,
		min_value = 1,
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

	
			