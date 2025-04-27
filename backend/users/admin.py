from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
    )
    list_editable = (
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
    )
    search_fields = ('email', 'username',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following',
    )
    list_editable = (
        'user',
        'following',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)