# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import BankLine


class BankLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankLine
        exclude = ['bank_account']
