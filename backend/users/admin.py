from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для кастомной модели User"""

    list_display = (
        'id', 'username', 'email',
        'first_name', 'last_name',
        'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {
            'fields': ('username', 'first_name', 'last_name', 'avatar')
        }),
        ('Права', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username',
                'first_name', 'last_name',
                'password1', 'password2',
                'is_staff', 'is_active'
            ),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для подписок"""

    list_display = ('id', 'user', 'subscribed_to', 'display_date')
    list_filter = ('user', 'subscribed_to')
    search_fields = (
        'user__username',
        'user__email',
        'subscribed_to__username',
        'subscribed_to__email'
    )

    def display_date(self, obj):
        return obj.user.date_joined.strftime('%Y-%m-%d')

    display_date.short_description = 'Дата подписки'