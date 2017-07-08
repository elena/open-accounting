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
    list_display = ['id', 'date', 'value', 'note', 'source']
    list_filter = ['source', 'date']
    inlines = [TransactionLineInline]

    def has_add_permission(self, request):
        return False


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
