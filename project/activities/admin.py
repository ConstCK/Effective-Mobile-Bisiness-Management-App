from django.contrib import admin
from .models import News, Meeting, Task, TaskStatus, TaskEstimation, Calendar

admin.site.register(News)
admin.site.register(Meeting)
admin.site.register(Task)
admin.site.register(TaskStatus)
admin.site.register(TaskEstimation)
admin.site.register(Calendar)
