from django.contrib import admin

from .models import BankTransaction, BankEntry


class BankEntryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'bank_transaction']
    list_filter = ['transaction__date']


class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'date', 'description',
                    'additional', 'value']
    list_filter = ['bank_account', 'bank_account__bank', 'date']


admin.site.register(BankTransaction, BankTransactionAdmin)
admin.site.register(BankEntry, BankEntryAdmin)
