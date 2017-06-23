# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Transaction, Line


class UserSerializer(serializers.HyperlinkedModelSerializer):
    transactions = serializers.HyperlinkedRelatedField(
        queryset=Transaction.objects.all(),
        view_name='transaction-detail', many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'transactions')


class LineSerializer(serializers.HyperlinkedModelSerializer):

    account = serializers.ReadOnlyField(source='account.name')

    class Meta:
        model = Line
        fields = ['account', 'value', 'note']


class TransactionSerializer(serializers.HyperlinkedModelSerializer):

    user = serializers.ReadOnlyField(source='owner.username')

    lines = LineSerializer(many=True)

    # Value is required false as this should be calculated by lines, with
    # necessary validation to ensure that it balances.
    value = serializers.DecimalField(
        required=False, max_digits=19, decimal_places=2)

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {
            'user': {'lookup_field': 'username'}
        }
