
from rest_framework import serializers

from .models import Profile, Country


class CountrySerializer(serializers.ModelSerializer):
    profiles_count = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ('id', 'name', 'profiles_count')

    def get_profiles_count(self, obj):
        return obj.profile_set.filter(is_public=True).count()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'last_name')


class PositionsCountSerializer(serializers.ModelSerializer):
    profiles_count = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ('position', 'profiles_count')
