from django.contrib import admin
from .models import Creditor, CreditorInvoice, CreditorPayment


class CreditorInvoiceAdmin(admin.ModelAdmin):
    list_filter = ['relation__entity']


admin.site.register(Creditor)
admin.site.register(CreditorInvoice, CreditorInvoiceAdmin)
admin.site.register(CreditorPayment)
