from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

# Create your models here.



# Used to provide descriptions for activities
ACTIVITY_DESCRIPTIONS = [
{
'act_type':'General Run',
'description':"""A general purpose run, maintaining a steady pace for 
a set time or distance"""
},
{
'act_type':'Intervals',
'description':'Repeated short distance runs with rest periods between'
},
{
'act_type':'Time Trial',
'description':'A fixed distance run with a specific goal time'
},
{
'act_type':'Cross Training',
'description':'Any non-running exercise activity.'},
]


# These are the pace options for activities which use them
# Choices field : [('DB VALUE','Readable'),]
PACES = ['Walk','Jog','Moderate Run','Hard Run','Maximum Effort']
PACE_LABELS = ['Walk','Easy Jog','Moderate Run','Hard Run','Maximum Effort']
PACE_CHOICES = [
	(PACES[0], PACE_LABELS[0]),
	(PACES[1], PACE_LABELS[1]),
	(PACES[2], PACE_LABELS[2]),
	(PACES[3], PACE_LABELS[3]),
	(PACES[4], PACE_LABELS[4]),
		]
# Perceived difficulty of the activity, used in building schedule. Used by 
# DB models and submission Form

DIFF_CHOICES = [
	('1','Easy'),
	('2','Moderate'),
	('3','Hard')
	]
# Day of week choices iterable for profile preferences.
DOW_CHOICES = [
	('Monday','Monday'),
	('Tuesday','Tuesday'),
	('Wednesday','Wednesday'),
	('Thursday','Thrusday'),
	('Friday','Friday'),
	('Saturday','Saturday'),
	('Sunday','Sunday')
	]

class Profile(models.Model):
	"""Stores information about user used to generate schedule and track
	statistics. Any information not related to a specific activity saved here"""
	owner = models.ForeignKey(
		User, 
		on_delete=models.CASCADE
		)
	# Python object converted to JSON which holds user's schedule information
	schedule = models.JSONField(null=True)
	last_exercise = models.DateField(null=True)
	# Day of week used as initial day for new schedule.
	start_day = models.CharField(
		max_length=10,
		default='Monday',
		choices=DOW_CHOICES
		)
	# Aimed for weekly distance (limit)
	mileage_target = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		null=True,
		blank=True,
		)
	# Mileage to date for current week
	mileage = models.DecimalField(null=True,max_digits=5,decimal_places=2)
	# How much mileage to add per week
	mileage_increment = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		default=0.0)


class Day:
	"""Contains information relating to a specific day"""	
	def __init__(self, date, rest=True, act_id=None, complete=False):
		# Set initial values
		# Is a rest day
		self.rest = rest
		if self.rest == False:
			# Activity the objrct relates to
			self.act_id = act_id
		# Calendar date the obj relates to
		self.date = date
		# Whether the activity has been completed
		self.complete = complete 	




# Parent class for all exercise types. All required fields / attributes here,
# exercise-specific fields / attributes / methods go on exercise sub-classes.
class Activity(models.Model):
	"""
	Parent class for all exercise types, contains attributes common to all,
	as well as anythin used by recommendation function
	"""
	class Meta:
		ordering = ['last_done']
		# By default returns objects with oldest first
	# User readable description of the activity for display on home screen & schedule
	name = models.CharField(max_length=40,default='namenlose')
	# User the activity is connected to
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	# Represents the total distance covered during the activity, used for tracking
	# mileage and in recommendation algorithm.
	distance = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		null=True,
		blank=True,
		)
	difficulty = models.CharField(
		max_length=1,
		choices=DIFF_CHOICES,
		default='2')
	# Date Activity was last performed
	last_done = models.DateField(null=True)
	# Whether act increases difficulty / length over time
	progressive = models.BooleanField(default=False)
	# How often (maximum) the activity should be done - value represents how many
	# days must pass before activity repeated in schedule - default is 7 and represents
	# the activity being done once per week
	frequency = models.PositiveSmallIntegerField(
		default=7,
		validators=[MaxValueValidator(365),MinValueValidator(1)]
		)
	# Used to store activity type in DB
	my_type = models.CharField(max_length=20,default='')
	def __str__(self):
		"""return string representation of the object"""
		return self.name



# Individual activity type models

# REQUIRED METHODS 
# ALL :
# setvalues(self) #Set initial values and NAME

# PROGRESSIVE ONLY :
# setgoals(self, post) 
# goal_prepop(self)

class PacedRun(Activity):
	"""Standard Taining run - holding a set pace for a set time or distance"""
	# User readable act_type and description
	act_type = ACTIVITY_DESCRIPTIONS[0]['act_type']
	description = ACTIVITY_DESCRIPTIONS[0]['description']
	# Determines whether the activity tracks time or distance
	PROG_CHOICES = [('TIME','Time(minutes)'),('DIST','Distance(km)'),] 
	prog_value = models.CharField(max_length=4, choices=PROG_CHOICES,default=PROG_CHOICES[0][1])
	
	# Progression values - amount by which activity values increased/ decreased
	prog_minutes = models.PositiveSmallIntegerField(null=True,blank=True)
	prog_distance = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)

	# Pace / relative exertion the activity is done at
	pace = models.CharField(
		max_length=18, 
		choices=PACE_CHOICES, 
		default=PACES[2])	
	# Length of activity time in minutes
	minutes = models.PositiveSmallIntegerField(
		null=True,
		blank=True,
		validators=[MaxValueValidator(720)]
		)
	# Goal time for activity - run length increases towards this value.
	goal_minutes = models.PositiveSmallIntegerField(
		null=True,
		blank=True,
		validators=[MaxValueValidator(720)]
		) 			
	# Goal distance for activity - increases towards this value if progressive.
	goal_distance = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)

	def setgoals(self,post):
		"""Sets Goal/progression values from form data"""
		goal_minutes = post.get('goal_minutes')
		goal_distance = post.get('goal_distance')
		# Form could be receiving decimal or integer inputs, needs to work with
		# either, so both are tried and result is converted to correct one.
		try:
			increment_value = int(post.get('increment_value'))
		except:
			increment_value = Decimal(post.get('increment_value'))	

		if goal_minutes:
			self.goal_minutes = int(goal_minutes)
			self.prog_minutes = int(increment_value)

		if goal_distance:
			self.goal_distance = Decimal(goal_distance)
			self.prog_distance = Decimal(increment_value)	

		return(self)

	def setvalues(self):
		"""Sets the name field for the activity, and checks / sets any other
		activity-specific fields"""
		# CASE 1- neither value given. Pace only name, return
		self.my_type = self.act_type
		if not self.minutes and not self.distance:
			self.name = f'{self.pace}'
			return self
		# CASE 2-BOTH values given, name based on type, return
		if self.minutes and self.distance:
			if self.prog_value == self.PROG_CHOICES[0][0]: #time
				self.name = f'{self.minutes} minute {self.pace}'
			else: #distance
				self.name = f'{self.distance} km {self.pace}'
			return self
		# CASE 3 - one or other given, return appropriate name and chekc type
		if self.minutes:
			self.prog_value = self.PROG_CHOICES[0][0] 
			self.name = f'{self.minutes} minute {self.pace}'
		else:
			self.prog_value = self.PROG_CHOICES[1][0]
			self.name = f'{self.distance} km {self.pace}'
		return self		

	def goal_prepop(self):
		"""returns a dictionary of values that can be used to prepopulate
		goal form for this activity"""
		prepop_dict = {}
		prepop_dict['goal_minutes'] = self.goal_minutes
		prepop_dict['goal_distance'] = self.goal_distance
		if self.prog_minutes:
			prepop_dict['increment_value'] = self.prog_minutes
		if self.prog_distance:
			prepop_dict['increment_value'] = self.prog_distance
		return prepop_dict	



		

class Intervals(Activity):
	"""Repeated short runs with a rest interval between each repetition."""
	# User readable act_type and description
	act_type = ACTIVITY_DESCRIPTIONS[1]['act_type']
	description = ACTIVITY_DESCRIPTIONS[1]['description']
	# Length of one repetition in metres
	rep_length = models.PositiveSmallIntegerField()
	# Number of reps
	rep_number = models.PositiveSmallIntegerField()
	# Goal number of reps
	rep_goal = models.PositiveSmallIntegerField(null=True,blank=True)
	# Number of reps to be added each time
	increment = models.PositiveSmallIntegerField(default=1)

	def setgoals(self,post):
		"""Sets Goal/progression values from form data"""
		rep_goal = post.get('rep_goal')
		increment = post.get('increment')
		if rep_goal:
			self.rep_goal = int(rep_goal)
		if increment:
			self.increment = int(increment)	
		return(self)

	def setvalues(self):
		"""Sets the name field for the activity"""
		self.my_type = self.act_type
		self.name = f'{self.rep_number} x {self.rep_length} m Intervals'
		return(self)	
	def goal_prepop(self):
		"""returns a dictionary of values that can be used to prepopulate
		goal form for this activity"""
		prepop_dict = {}
		prepop_dict['rep_goal'] = self.rep_goal
		prepop_dict['increment'] = self.increment


		return prepop_dict
	

class TimeTrial(Activity):
	"""Attempting to run  a set distance in a target time"""
	# User readable act_type and description
	act_type = ACTIVITY_DESCRIPTIONS[2]['act_type']
	description = ACTIVITY_DESCRIPTIONS[2]['description']
	# Time (in seconds) of activity 
	time = models.PositiveSmallIntegerField(blank=True,null=True)
	# Goal target time
	goal_time = models.PositiveSmallIntegerField(blank=True,null=True)
	# Number of seconds to be taken off time each time exercise done
	prog_time = models.PositiveSmallIntegerField(blank=True,null=True)

	def setgoals(self,post):
		"""Sets Goal/progression values from form data"""
		goal_minutes = post.get('goal_minutes')
		goal_seconds = post.get('goal_seconds')
		inc_seconds = post.get('inc_seconds')
		time = 0
		if goal_minutes:
			time = int(goal_minutes) * 60
		if goal_seconds:
			time += int(goal_seconds)
		if time:
			self.goal_time = time	
		if inc_seconds:
			self.prog_time = inc_seconds		
		return(self)

	def setvalues(self):
		"""Sets the name field for the activity"""
		self.my_type = self.act_type
		self.name = f'{self.distance}km Time Trial'
		return(self)	

	def goal_prepop(self):
		"""returns a dictionary of values that can be used to prepopulate
		goal form for this activity"""
		prepop_dict = {}
		prepop_dict['goal_minutes'] = (self.goal_time // 60)
		prepop_dict['goal_seconds'] = (self.goal_time % 60)
		prepop_dict['inc_seconds'] = self.prog_time

		return prepop_dict
	


class CrossTrain(Activity):
	"""Any other exercise type, which the user wants to be taken into account
	by scheduling algorithm"""
	# User readable act_type and description
	act_type = ACTIVITY_DESCRIPTIONS[3]['act_type']
	description = ACTIVITY_DESCRIPTIONS[3]['description']
	exercise_type = models.CharField(max_length=30,default='Cross Training')


	def setvalues(self):
		"""Sets the name field for the activity"""
		if not self.exercise_type:
			self.exercise_type = 'Cross Training'
		self.name = self.exercise_type
		self.my_type = self.act_type
		return(self)
	
	

	

