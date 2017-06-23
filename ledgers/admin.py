from django.contrib import admin

from .models import Transaction, Line, Account


class TransactionLineInline(admin.TabularInline):
    model = Line


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_filter = ['source']
    inlines = [
        TransactionLineInline,
    ]


class AccountAdmin(admin.ModelAdmin):
    list_display = ('get_code', 'number', 'element', 'name')
    list_filter = ['element']
    model = Account


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
