# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import viewsets

from .models import Transaction
from .serializers import (TransactionSerializer, UserSerializer)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
