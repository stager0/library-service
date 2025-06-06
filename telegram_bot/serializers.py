from rest_framework import serializers

class TelegramSerializer(serializers.Serializer):
    update_id = serializers.IntegerField()
    message = serializers.JSONField()
