from django.contrib import admin
from .models import Plan, UserSubscription, DailyFreeQuota, Coupon


admin.site.register(Plan)
admin.site.register(UserSubscription)
admin.site.register(DailyFreeQuota)
admin.site.register(Coupon)
