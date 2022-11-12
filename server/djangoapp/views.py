from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, DealerReview, CarModel, CarMake
from .restapis import get_dealers_from_cf,get_dealer_reviews_from_cf,post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
#week 1 T4
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#Week 1 T4
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
#week 2 t5
def login_request(request):
    context = {}
    url = "https://41165407-fde5-4d7f-9595-a7ccd5c0c021-bluemix.cloudantnosqldb.appdomain.cloud/api/dealership"
    dealerships = get_dealers_from_cf(url)
    # Concat all dealer's short name
    context["dealership_list"]=dealerships
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['pword']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            # If not, return to login page again
            context["message"]="Username or password is incorrect."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


# Create a `logout_request` view to handle sign out request
# Week 2 T5
def logout_request(request):
    context = {}
    url = "https://41165407-fde5-4d7f-9595-a7ccd5c0c021-bluemix.cloudantnosqldb.appdomain.cloud/api/dealership"
    dealerships = get_dealers_from_cf(url)
    # Concat all dealer's short name
    context["dealership_list"]=dealerships
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return render(request, 'djangoapp/index.html', context)


# Create a `registration_request` view to handle sign up request
#week 2 T7
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['pword']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context["message"]="Account could not be created try again."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context={}
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/05174de9-c4f2-4d8f-a22f-b17713e83492/dealership-package/get-dealership"
        apikey="_xKRLnH-xVpGqx9u0VBB3dZUTVxhZ8JNVyxYY6ooCjB2"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        context["dealership_list"]=dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context={}
    url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/05174de9-c4f2-4d8f-a22f-b17713e83492/dealership-package/get-review"
    apikey="_xKRLnH-xVpGqx9u0VBB3dZUTVxhZ8JNVyxYY6ooCjB2"
    #print(dealer_id)
    # Get dealers from the URL
    dealer_details = get_dealer_reviews_from_cf(url,dealer_id)
    context["dealer_id"]=dealer_id
    context["reviews"]=dealer_details
    return render(request, 'djangoapp/dealer_details.html', context)
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    # If it is a GET request, just render the add_review page
    if request.method == 'GET':
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/05174de9-c4f2-4d8f-a22f-b17713e83492/dealership-package/get-dealership"
        # Get dealers from the URL
        context = {
            "dealer_id": dealer_id,
            "dealer_name": get_dealers_from_cf(url)[dealer_id-1].full_name,
            "cars": CarModel.objects.all()
        }
        #print(context)
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if (request.user.is_authenticated):
            review = dict()
            review["id"]=0#placeholder
            review["name"]=request.POST["name"]
            review["dealership"]=dealer_id
            review["review"]=request.POST["content"]
            if ("purchasecheck" in request.POST):
                review["purchase"]=True
            else:
                review["purchase"]=False
            print(request.POST["car"])
            if review["purchase"] == True:
                car_parts=request.POST["car"].split("|")
                review["purchase_date"]=request.POST["purchase_date"] 
                review["car_make"]=car_parts[0]
                review["car_model"]=car_parts[1]
                review["car_year"]=car_parts[2]

            else:
                review["purchase_date"]=None
                review["car_make"]=None
                review["car_model"]=None
                review["car_year"]=None
            json_result = post_request("https://eu-gb.functions.appdomain.cloud/api/v1/web/05174de9-c4f2-4d8f-a22f-b17713e83492/dealership-package/post-review", review, dealerId=dealer_id)
            print(json_result)
            if "error" in json_result:
                context["message"] = "ERROR: Review was not submitted."
            else:
                context["message"] = "Review was submited"
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
