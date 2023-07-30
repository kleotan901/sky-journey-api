from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import EmailConfirmationToken
from user.serializers import UserSerializer, UserListSerializer
from user.tasks import send_email


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserListSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)


    def get_object(self):
        return self.request.user


class SendEmailConfirmationAPIView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        user = request.user
        token = EmailConfirmationToken.objects.create(user=user)
        send_email.delay(user.email, token.id, user.id)
        return Response({"message": "Email was sent"}, status.HTTP_201_CREATED)

    def email_verification(self, request):
        token_id = request.GET["token_id"]
        try:
            token = EmailConfirmationToken.objects.get(id=token_id)
            user = token.user
            if user.is_email_confirmed:
                return Response(
                    {"message": "This email has already been verified"}, status.HTTP_200_OK
                )
            user.is_email_confirmed = True
            user.save()
            return Response({"message": "Email confirmed"}, status.HTTP_200_OK)
        except EmailConfirmationToken.DoesNotExist:
            return Response({"message": "Not Confirm"}, status.HTTP_400_BAD_REQUEST)
