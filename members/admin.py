from django.contrib import admin
from members.models import Class,Student,GradingConfig,UserProfile

# Register your models here.
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(GradingConfig)
admin.site.register(UserProfile)