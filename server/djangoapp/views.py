import json
import logging
from datetime import date
from functools import wraps
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import CarModel
from .restapis import get_request, post_review, analyze_review_sentiments

logger = logging.getLogger(__name__)

def api_errors(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        try:
            return view(*args, **kwargs)
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            return JsonResponse({"error":"Invalid or incomplete request"},status=400)
        except requests.RequestException:
            logger.exception("Backend service unavailable")
            return JsonResponse({"error":"A backend service is unavailable. Please try again."},status=502)
    return wrapped

@require_GET
@ensure_csrf_cookie
def session(request):
    return JsonResponse({"userName":request.user.username if request.user.is_authenticated else None})

@require_POST
@api_errors
def login_user(request):
    data = json.loads(request.body)
    user = authenticate(request,username=data["userName"],password=data["password"])
    if user is None:
        return JsonResponse({"error":"Invalid username or password"},status=401)
    login(request,user)
    return JsonResponse({"userName":user.username,"status":"Authenticated"})

@require_POST
def logout_request(request):
    logout(request)
    return JsonResponse({"status":"Logged out"})

@require_POST
@api_errors
def registration(request):
    data=json.loads(request.body)
    username=data["userName"].strip()
    if not username or len(username)>150:
        return JsonResponse({"error":"Choose a username of 1–150 characters"},status=400)
    try:
        User.username_validator(username)
        validate_password(data["password"])
        user=User.objects.create_user(username=username,password=data["password"],first_name=data.get("firstName",""),last_name=data.get("lastName",""),email=data.get("email",""))
    except ValidationError as exc:
        return JsonResponse({"error":" ".join(exc.messages)},status=400)
    except IntegrityError:
        return JsonResponse({"error":"This username is already taken"},status=409)
    login(request,user)
    return JsonResponse({"userName":user.username,"status":"Authenticated"},status=201)

@require_GET
@api_errors
def get_dealerships(request,state="All"):
    endpoint="fetchDealers" if state=="All" else "fetchDealers/"+requests.utils.quote(state,safe="")
    return JsonResponse({"status":200,"dealers":get_request(endpoint)})

@require_GET
@api_errors
def get_dealer_details(request,dealer_id):
    dealer=get_request(f"fetchDealer/{dealer_id}")
    return JsonResponse({"status":200,"dealer":dealer})

@require_GET
@api_errors
def get_dealer_reviews(request,dealer_id):
    reviews=get_request(f"fetchReviews/dealer/{dealer_id}")
    for review in reviews:
        review["sentiment"]=analyze_review_sentiments(review["review"])
    return JsonResponse({"status":200,"reviews":reviews})

@require_GET
def get_cars(request):
    return JsonResponse({"CarModels":[{"id":c.id,"CarMake":c.car_make.name,"CarModel":c.name,"year":c.year,"type":c.type} for c in CarModel.objects.select_related("car_make").all()]})

@require_POST
@api_errors
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error":"Please sign in to post a review"},status=401)
    data=json.loads(request.body)
    review=str(data["review"]).strip()
    dealer=int(data["dealership"])
    year=int(data["car_year"])
    purchase_date=date.fromisoformat(data["purchase_date"])
    if not review or len(review)>5000 or not 2015<=year<=2023 or purchase_date>date.today():
        return JsonResponse({"error":"Check review text, purchase date and car year (2015–2023)"},status=400)
    car=CarModel.objects.select_related("car_make").filter(id=int(data["car_id"])).first()
    if car is None or not get_request(f"fetchDealer/{dealer}"):
        return JsonResponse({"error":"Car model or dealer not found"},status=404)
    payload={"name":request.user.get_full_name() or request.user.username,"dealership":dealer,"review":review,"purchase":bool(data.get("purchase",True)),"purchase_date":purchase_date.isoformat(),"car_make":car.car_make.name,"car_model":car.name,"car_year":year}
    result=post_review(payload)
    return JsonResponse({"status":200,"review":result},status=201)
