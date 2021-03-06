from rest_framework import serializers

from auto_report.models import Car, GpsPoint, Session, User
from auto_report.tasks import create_roads


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('card_hash', 'id', 'is_authorised_to_change_mode')
        read_only_fields = ('card_hash', 'id', 'is_authorised_to_change_mode')


class GpsPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = GpsPoint
        fields = ('datetime', 'latitude', 'longitude', 'altitude', 'speed', 'track')


class SessionSerializer(serializers.ModelSerializer):

    gps_points = GpsPointSerializer(many=True)
    car = serializers.SlugRelatedField(slug_field='vin_code', queryset=Car.objects.all())
    users = serializers.PrimaryKeyRelatedField(allow_null=True, many=True, queryset=User.objects.all())

    class Meta:
        model = Session
        fields = ('distance', 'gps_points', 'mode', 'start_date', 'stop_date', 'users', 'car')

    def create(self, validated_data):
        raw_gps_points = validated_data.pop('gps_points', None)
        users = validated_data.pop('users', None)
        session = Session.objects.create(**validated_data)
        if users:
            #session.users.add(users)
            session.users.add(*users)
        if raw_gps_points:
            GpsPoint.objects.bulk_create([
                GpsPoint(session=session, **gps_point_data) for gps_point_data in raw_gps_points
            ])
        create_roads.delay(session.id)
        return session
