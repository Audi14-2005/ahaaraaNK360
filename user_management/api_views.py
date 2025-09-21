from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile, PatientProfile
from .serializers import UserProfileSerializer, PatientProfileSerializer
import logging

logger = logging.getLogger(__name__)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return user profiles for the authenticated user"""
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            user_type = request.data.get('user_type', 'patient')
            
            if not username or not email or not password:
                return Response({
                    'success': False,
                    'error': 'Username, email, and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return Response({
                    'success': False,
                    'error': 'Username already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'error': 'Email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create user profile
            user_profile = UserProfile.objects.create(
                user=user,
                user_type=user_type
            )
            
            # Create patient profile if user is a patient
            if user_type == 'patient':
                PatientProfile.objects.create(user_profile=user_profile)
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'token': token.key,
                'user_profile': UserProfileSerializer(user_profile).data
            })
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login user and return token"""
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response({
                    'success': False,
                    'error': 'Username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is None:
                return Response({
                    'success': False,
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get or create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Get user profile
            try:
                user_profile = UserProfile.objects.get(user=user)
                profile_data = UserProfileSerializer(user_profile).data
            except UserProfile.DoesNotExist:
                profile_data = None
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'token': token.key,
                'user_profile': profile_data
            })
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user and delete token"""
        try:
            # Delete the user's token
            Token.objects.filter(user=request.user).delete()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            })
            
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for PatientProfile model"""
    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return patient profiles for the authenticated user"""
        if self.request.user.userprofile.user_type == 'patient':
            return PatientProfile.objects.filter(user_profile__user=self.request.user)
        elif self.request.user.userprofile.user_type == 'dietitian':
            return PatientProfile.objects.filter(assigned_doctor=self.request.user.userprofile)
        return PatientProfile.objects.none()
