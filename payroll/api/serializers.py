from rest_framework import serializers


class UploadCSVSerializer(serializers.Serializer):
    inputs_file = serializers.FileField()

    class Meta:
        fields = ('inputs_file',)
