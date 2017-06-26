from django.contrib import admin

from .models import Account, Transaction, Line


class AccountAdmin(admin.ModelAdmin):
    list_display = ('get_code', 'number', 'element', 'name')
    list_filter = ['element']
    model = Account


class TransactionLineInline(admin.TabularInline):
    model = Line


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_filter = ['source']
    inlines = [
        TransactionLineInline,
    ]


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
