# url aths for Planner app
from django.urls import path

from . import views

app_name = 'planner'
urlpatterns = [
	path('tests/',views.testview,name='testing'),
	path('',views.home,name='home'),
	path('addnew/',views.add_new,name='addnew'),
	path('addnew/<str:act_type>/',views.add_new,name='addnew'),
	path('setgoal/',views.setgoal,name='setgoal'),
	# Delete an Activity instance
	path('delete/<int:act_id>/',views.delete,name='delete'),
	# Edit details of an activity
	path('edit/<int:act_id>/',views.edit,name='edit'),
	# Submit details of completed activity
	
	path('submit/<int:act_id>/<str:date_iso>/',views.submit,name='submitdate'),
	# Submit details of rest day
	path('submit/<str:date_iso>/',views.restdate,name='restdate'),
	path('generate/',views.generate_plan,name='generate'),
	path('settings/',views.settings,name='settings'),
	path('history/',views.view_history,name='history'),
	]

	# path('delete/',views.delete,name='delete'),