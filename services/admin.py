from django.contrib import admin
from services.models import *
admin.site.register(Category)
admin.site.register(SLAConfig)
admin.site.register(ServiceRequest)
admin.site.register(RequestComment)
admin.site.register(RequestHistory)
