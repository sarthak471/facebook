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
from .helper import FriendRequestRateThrottle, helper_response
import logging

logger = logging.getLogger("django")


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
            logger.info(f"User created successfully: {serializer.data}")
            return Response(
                helper_response(
                    True,
                    serializer.data,
                    status.HTTP_201_CREATED,
                    "User created successfully",
                )
            )
        else:
            logger.error(f"Failed to create user: {serializer.errors}")
            return Response(
                helper_response(
                    False,
                    serializer.errors,
                    status.HTTP_400_BAD_REQUEST,
                    "Failed to create user",
                )
            )


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
    logger.debug("Executing register user api")
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        logger.info(f"User logged in successfully: {user}")
        return Response(
            helper_response(
                True,
                {"token": token.key},
                status.HTTP_200_OK,
                "User logged in successfully",
            )
        )
    else:
        logger.error(f"Failed to log in user: {serializer.errors}")
        return Response(
            helper_response(
                False,
                serializer.errors,
                status.HTTP_400_BAD_REQUEST,
                "Failed to log in user",
            )
        )


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


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
    logger.info(f"Search users successful for query: {search_query}")
    return Response(
        helper_response(
            True, serializer.data, status.HTTP_200_OK, "Search users successful"
        )
    )


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
        error_message = "You cannot send a friend request to yourself."
        logger.error(error_message)
        return Response(
            helper_response(False, None, status.HTTP_400_BAD_REQUEST, error_message)
        )

    friendships = Friendship.objects.filter(
        from_user_id=request.user, to_user=user_id
    ).first()

    if friendships:
        if friendships.friend_status:
            error_message = "You both are already friends."
            logger.error(error_message)
            return Response(
                helper_response(False, None, status.HTTP_400_BAD_REQUEST, error_message)
            )
        elif friendships.request_status:
            error_message = "Friend request already sent."
            logger.error(error_message)
            return Response(
                helper_response(False, None, status.HTTP_400_BAD_REQUEST, error_message)
            )
        elif friendships.reject_status:
            friendships.friend_status = False
            friendships.request_status = True
            friendships.reject_status = False
            friendships.save()
            logger.info("Friend request sent successfully.")
            return Response(
                helper_response(
                    True,
                    {"status": "Friend request sent."},
                    status.HTTP_201_CREATED,
                    "Friend request sent successfully",
                )
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
            logger.info(f"Friend request sent successfully to user {to_user}.")
            return Response(
                helper_response(
                    True,
                    {"status": "Friend request sent."},
                    status.HTTP_201_CREATED,
                    "Friend request sent successfully",
                )
            )
        else:
            error_message = "Failed to send friend request."
            logger.error(error_message)
            return Response(
                helper_response(False, None, status.HTTP_400_BAD_REQUEST, error_message)
            )
    except User.DoesNotExist:
        error_message = "User not found."
        logger.error(error_message)
        return Response(
            helper_response(False, None, status.HTTP_404_NOT_FOUND, error_message)
        )


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
            error_message = "You are already friends."
            logger.error(error_message)
            return Response(
                helper_response(False, None, status.HTTP_400_BAD_REQUEST, error_message)
            )
        friendship.friend_status = True
        friendship.request_status = False
        friendship.reject_status = False
        friendship.save()
        to_user = User.objects.filter(id=user_id).first()
        if not to_user:
            error_message = "Corresponding user does not exist."
            logger.error(error_message)
            return Response(
                helper_response(
                    False, None, status.HTTP_500_INTERNAL_SERVER_ERROR, error_message
                )
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
            error_message = "Something went wrong."
            logger.error(error_message)
            return Response(
                helper_response(
                    False, None, status.HTTP_500_INTERNAL_SERVER_ERROR, error_message
                )
            )
        logger.info("Friend request accepted successfully.")
        return Response(
            helper_response(
                True,
                {"status": "Friend request accepted."},
                status.HTTP_200_OK,
                "Friend request accepted successfully",
            )
        )
    except Friendship.DoesNotExist:
        error_message = "Friend request not found."
        logger.error(error_message)
        return Response(
            helper_response(False, None, status.HTTP_404_NOT_FOUND, error_message)
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
            error_message = "Friend request not found."
            logger.error(error_message)
            return Response(
                helper_response(False, None, status.HTTP_404_NOT_FOUND, error_message)
            )
        if friendship.friend_status:
            error_message = "You are already friends."
            logger.error(error_message)
            return Response(
                helper_response(False, None, status.HTTP_400_BAD_REQUEST, error_message)
            )
        friendship.friend_status = False
        friendship.request_status = False
        friendship.reject_status = True
        friendship.save()
        logger.info("Friend request rejected successfully.")
        return Response(
            helper_response(
                True,
                {"detail": "Friend request rejected."},
                status.HTTP_200_OK,
                "Friend request rejected successfully",
            )
        )
    except Friendship.DoesNotExist:
        error_message = "Friend request not found."
        logger.error(error_message)
        return Response(
            helper_response(False, None, status.HTTP_404_NOT_FOUND, error_message)
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
    logger.info("List of friends retrieved successfully.")
    return Response(
        helper_response(
            True,
            serializer.data,
            status.HTTP_200_OK,
            "List of friends retrieved successfully",
        )
    )


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
    logger.info("List of pending friend requests retrieved successfully.")
    return Response(
        helper_response(
            True,
            serializer.data,
            status.HTTP_200_OK,
            "List of pending friend requests retrieved successfully",
        )
    )
