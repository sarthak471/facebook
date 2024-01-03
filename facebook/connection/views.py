from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import LoginSerializer
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer
from django.db.models import Q
from .models import Friendship
from rest_framework import status, viewsets
from rest_framework.decorators import action
from .serializers import (
    FriendshipSerializer,
    PendingListResponseSerializer,
    FriendShipListResponseSerializer,
)
from rest_framework.permissions import AllowAny
from .helper import FriendRequestRateThrottle


@api_view(["POST"])
@permission_classes([AllowAny])
def create_user(request):
    """
    endpoint - http://localhost:8000/connection/login/
    Content-Type: application/json
    body - {
        "username": "kong",
        "password": "kong",
        "email" :"kong@gmail.com",
        "first_name":"kong",
        "last_name":"kong"
    }
    """
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    """
        endpoint - http://localhost:8000/connection/create/
        Content-Type: application/json
        body - {
            "username": "kong",
            "password": "kong"
    }
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def search_users(request):
    """
    endpoint -http://127.0.0.1:8000/connection/search-users/?search=sarthak
    Authorization(Inside Header): Token 991c5df483255e0c0a3d8b8bb6e246d1a5e93aab
    Content-Type: application/json
    """
    search_query = request.query_params.get("search", None)
    if search_query:
        users = User.objects.filter(
            Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )
    else:
        users = User.objects.none()

    paginator = StandardResultsSetPagination()
    paginated_users = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@throttle_classes([FriendRequestRateThrottle])
def send_friend_request(request, user_id):
    """
    endpoint - http://127.0.0.1:8000/connection/send_request/5("user id of the person whom you want to send request")/
    Authorization(Inside Header): Token 991c5df483255e0c0a3d8b8bb6e246d1a5e93aab
    Content-Type: application/json
    """
    if request.user.id == int(user_id):
        return Response(
            {"error": "You cannot send a friend request to yourself."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    friendships = Friendship.objects.filter(
        from_user_id=request.user, to_user=user_id
    ).first()
    if friendships:
        if friendships.friend_status:
            return Response(
                {"status": "You both are already Friend."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif friendships.request_status:
            return Response(
                {"status": "Friend request already sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif friendships.reject_status:
            friendship.friend_status = False
            friendship.request_status = True
            friendship.reject_status = False
            friendship.save()
            return Response(
                {"status": "Friend request sent."}, status=status.HTTP_201_CREATED
            )

    try:
        to_user = User.objects.get(pk=user_id)
        friendship, created = Friendship.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={
                "friend_status": False,
                "request_status": True,
                "reject_status": False,
            },
        )
        if created:
            return Response(
                {"status": "Friend request sent."}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "Friend request already sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def accept_friend_request(request, user_id):
    """
    endpoint - http://127.0.0.1:8000/connection/accept_request/5("user id of the person whom request you want to accept")/
    Authorization(Inside Header): Token 991c5df483255e0c0a3d8b8bb6e246d1a5e93aab
    Content-Type: application/json
    """
    try:
        friendship = Friendship.objects.filter(
            from_user_id=user_id, to_user=request.user
        ).get()
        if friendship.friend_status:
            return Response(
                {"error": "You are already Friend."}, status=status.HTTP_404_NOT_FOUND
            )
        friendship.friend_status = True
        friendship.request_status = False
        friendship.reject_status = False
        friendship.save()
        to_user = User.objects.filter(id=user_id).first()
        if not to_user:
            return Response(
                {"error": "Corresponding user does not exist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        reversed, created = Friendship.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={
                "friend_status": True,
                "request_status": False,
                "reject_status": False,
            },
        )
        if not created:
            return Response(
                {"status": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {"status": "Friend request accepted."}, status=status.HTTP_200_OK
        )
    except Friendship.DoesNotExist:
        return Response(
            {"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(e)
        return Response(
            {"error": "Something went wrong."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def reject_friend_request(request, user_id):
    """
    endpoint - http://127.0.0.1:8000/connection/reject_request/5("user id of the person whom request you want to reject")/
    Authorization(Inside Header): Token 991c5df483255e0c0a3d8b8bb6e246d1a5e93aab
    Content-Type: application/json
    """
    try:
        friendship = Friendship.objects.filter(
            from_user_id=user_id, to_user=request.user
        ).get()
        if not friendship:
            return Response(
                {"error": " Friend request not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if friendship.friend_status:
            return Response(
                {"error": " You are already friend"}, status=status.HTTP_400_BAD_REQUEST
            )
        friendship.friend_status = False
        friendship.request_status = False
        friendship.reject_status = True
        friendship.save()
        return Response(
            {"detail": "Friend request rejected."}, status=status.HTTP_200_OK
        )
    except Friendship.DoesNotExist:
        return Response(
            {"detail": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def list_friends(request):
    """
    endpoint - http://127.0.0.1:8000/connection/friends
    Authorization(Inside Header): Token 991c5df483255e0c0a3d8b8bb6e246d1a5e93aab
    Content-Type: application/json
    """
    friendships = Friendship.objects.filter(
        from_user_id=request.user, friend_status=True
    )
    serializer = FriendShipListResponseSerializer(friendships, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def pending_request(request):
    """
    endpoint - http://127.0.0.1:8000/connection/pending
    Authorization(Inside Header): Token 991c5df483255e0c0a3d8b8bb6e246d1a5e93aab
    Content-Type: application/json
    """
    friendships = Friendship.objects.filter(to_user=request.user, request_status=True)
    serializer = PendingListResponseSerializer(friendships, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
