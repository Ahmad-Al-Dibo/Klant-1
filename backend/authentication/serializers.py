from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'profile_picture_url'
        ]
        read_only_fields = [
            'id', 'is_staff', 'is_superuser', 'date_joined',
            'last_login'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username
    
    def get_profile_picture_url(self, obj):
        """Get profile picture URL if exists"""
        # Assuming you have a UserProfile model with profile_picture field
        try:
            if hasattr(obj, 'profile') and obj.profile.profile_picture:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.profile.profile_picture.url)
                return obj.profile.profile_picture.url
        except:
            pass
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        
        # Check if username exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        
        # Check if email exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
        
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=True
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        # Create user profile if you have one
        # UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Try to authenticate with username or email
        user = None
        
        # Check if input is email
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid login credentials")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        # Update last login
        user.last_login = timezone.now()
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        attrs['user'] = user
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)
        
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'current_password', 'new_password'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
    def validate(self, attrs):
        """Validate password change"""
        if attrs.get('new_password') and not attrs.get('current_password'):
            raise serializers.ValidationError({
                "current_password": "Current password is required to set a new password."
            })
        
        if attrs.get('current_password') and attrs.get('new_password'):
            user = self.context['request'].user
            if not user.check_password(attrs['current_password']):
                raise serializers.ValidationError({
                    "current_password": "Current password is incorrect."
                })
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update user profile"""
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        
        # Update password if provided
        new_password = validated_data.get('new_password')
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        return instance


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    new_password = serializers.CharField(required=True, validators=[validate_password])
    token = serializers.CharField(required=True)
    uidb64 = serializers.CharField(required=True)


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for user lists"""
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name',
            'is_active', 'is_staff', 'role', 'date_joined'
        ]
    
    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username
    
    def get_role(self, obj):
        if obj.is_superuser:
            return "Superuser"
        elif obj.is_staff:
            return "Staff"
        else:
            return "User"


class ChangePasswordSerializer(serializers.Serializer):
    """
    Enhanced serializer for password change with additional validations.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        
        if not user.check_password(value):
            raise serializers.ValidationError({
                "old_password": "The current password you entered is incorrect."
            })
        
        return value
    
    def validate_new_password(self, value):
        """Additional custom password validation"""
        user = self.context['request'].user
        
        # Check if password contains username
        if user.username.lower() in value.lower():
            raise serializers.ValidationError(
                "Password should not contain your username."
            )
        
        # Check if password contains email username
        email_username = user.email.split('@')[0].lower()
        if email_username and email_username in value.lower():
            raise serializers.ValidationError(
                "Password should not contain your email username."
            )
        
        # Check for common password patterns
        common_patterns = ['123456', 'password', 'qwerty', 'admin']
        for pattern in common_patterns:
            if pattern in value.lower():
                raise serializers.ValidationError(
                    "Password is too common. Choose a stronger password."
                )
        
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match and are not the same as old"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password_confirm": "The two new password fields didn't match."
            })
        
        # Check that new password is different from old password
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                "new_password": "New password must be different from your current password."
            })
        
        # Check password similarity with old password (optional)
        # You can add more sophisticated similarity checks here
        
        return attrs
    
    def save(self, **kwargs):
        """Save the new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Optional: Log password change
        # PasswordChangeLog.objects.create(user=user)
        
        return user