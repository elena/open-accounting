# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.views import generic

from rest_framework import permissions
from rest_framework import viewsets

from .serializers import (TransactionSerializer, UserSerializer)
from .models import Account, Transaction, Line


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AccountListView(generic.list.ListView):

    model = Account


