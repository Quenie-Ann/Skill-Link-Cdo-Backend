from django.contrib import admin
from .models import User, WorkerProfile, JobRequest

admin.site.register(User)
admin.site.register(WorkerProfile)
admin.site.register(JobRequest)