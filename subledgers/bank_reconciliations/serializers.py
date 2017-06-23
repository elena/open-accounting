# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import BankTransaction


class BankTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankTransaction
        exclude = ['bank_account']
