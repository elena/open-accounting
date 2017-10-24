from django.contrib import admin

from .models import BankLine, BankEntry


class BankEntryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'bank_line']
    list_filter = ['transaction__date']


class BankLineAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'date', 'description',
                    'additional', 'value']
    list_filter = ['bank_account', 'bank_account__bank', 'date']


admin.site.register(BankLine, BankLineAdmin)
admin.site.register(BankEntry, BankEntryAdmin)
