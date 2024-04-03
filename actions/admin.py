from django.contrib import admin

from .models import Action

class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'date')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('action', 'user__username')
    ordering = ('-date',)
    list_per_page = 20

    site_header = 'Мой крутой админ-сайт'
    site_title = 'Администрирование'


admin.site.register(Action, ActionAdmin)
