# -*- coding: utf-8 -*-
from rest_framework import serializers
from . import utils
from .models import Entity


class EntitySerializer(serializers.ModelSerializer):

    code = serializers.CharField(required=False)

    class Meta:
        model = Entity
        fields = '__all__'
