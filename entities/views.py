# from django.shortcuts import render
from rest_framework import permissions
# from rest_framework import renderers
from rest_framework import viewsets
from .models import Entity
from .serializers import EntitySerializer
# from .utils import generate_unique_code


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (permissions.IsAdminUser,)
