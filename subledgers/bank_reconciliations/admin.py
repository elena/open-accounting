from django.contrib import admin

from .models import BankTransaction


class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'date', 'description',
                    'additional', 'value']
    list_filter = ['bank_account', 'bank_account__bank', 'date']

admin.site.register(BankTransaction, BankTransactionAdmin)
