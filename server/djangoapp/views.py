# Uncomment the required imports before adding the code

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create a `login_user` view to handle sign-in request
@csrf_exempt
def login_user(request):
    """Authenticate and log in a user."""
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]

    # Try to authenticate the user
    user = authenticate(username=username, password=password)

    if user:
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
    else:
        response_data = {"userName": username, "status": "Failed"}

    return JsonResponse(response_data)


# Create a `logout_request` view to handle sign-out request
def logout_request(request):
    """Log out the user."""
    logout(request)
    return JsonResponse({"userName": ""})


# Create a `registration` view to handle sign-up requests
@csrf_exempt
def registration(request):
    """Register a new user."""
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    try:
        User.objects.get(username=username)
        return JsonResponse({
            "userName": username,
            "error": "Already Registered"})
    except User.DoesNotExist:
        logger.debug(f"{username} is a new user")

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        email=email,
    )
    login(request, user)
    return JsonResponse({
        "userName": username,
        "status": "Authenticated"})


# Update the `get_dealerships` function to return a list of dealerships
def get_dealerships(request, state="All"):
    """Fetch dealership details, filtered by state if provided."""
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    """Fetch and analyze dealer reviews."""
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)

        for review in reviews:
            try:
                sentiment_response = analyze_review_sentiments(
                    review["review"]
                    )
                review["sentiment"] = sentiment_response.get(
                    "sentiment", "Unknown"
                    )
            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")

        return JsonResponse({"status": 200, "reviews": reviews})

    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_details(request, dealer_id):
    """Fetch dealer details."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})

    return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    """Add a review if the user is authenticated."""
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error posting review: {e}")
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review"
                })

    return JsonResponse({"status": 403, "message": "Unauthorized"})
