from rest_framework import serializers
from apps.authentication.models.user import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'username', 'role'
            'is_active', 'is_email_verified'
        ]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        data['display_name'] = instance.username
        data['profile_url'] = f'https://bookinghub.com/{instance.username}'
        
        if not self.context.get('show_role', False):
            data.pop('role', None)
            
        return data
