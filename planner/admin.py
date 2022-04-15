from django.contrib import admin
from .models import (Activity, PacedRun, Intervals, TimeTrial, CrossTrain, Profile,
	CompletedAct)
admin.site.register(Activity)
admin.site.register(PacedRun)
admin.site.register(Intervals)
admin.site.register(TimeTrial)
admin.site.register(CrossTrain)
admin.site.register(Profile)
admin.site.register(CompletedAct)

# Register your models here.
