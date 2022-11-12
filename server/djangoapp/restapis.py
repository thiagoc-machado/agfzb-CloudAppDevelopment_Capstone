import requests
import json

from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    #print(kwargs)
    print("GET from {} ".format(url))
    json_data={}
    try:
        if "apikey" in kwargs:
            response = requests.get(url, headers={'Content-Type':'application/json'}, params=kwargs, auth=HTTPBasicAuth("apikey", kwargs["apikey"]))
        else:
            response = requests.get(url, headers={'Content-Type':'application/json'}, params=kwargs)

        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        #print(json_data)
    except Exception as e:
        print("Error " ,e)
    
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(url)
    print(payload)
    print(kwargs)
    try:
        response = requests.post(url, params=kwargs, json=payload)
    except Exception as e:
        print("Error" ,e)
    print("Status Code ", {response.status_code})
    data = json.loads(response.text)
    return data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    #print(json_result)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealers["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results
#Coding practice: create a get_dealer_by_id or get_dealers_by_state method in restapis.py. HINT, the only difference from the get_dealers_from_cf method is adding a dealer id or state URL parameter argument when calling the def get_request(url, **kwargs): method such as get_request(url, dealerId=dealerId).


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    
    if "entries" in json_result:
        reviews = json_result["entries"]
        # For each review object
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=analyze_review_sentiments(review["review"]),
                id=review['id']
                )
            results.append(review_obj)
    #print(results[0])
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview, **kwargs):
    API_KEY="qHY59TRRsW6rPG4a-SP2pia-shPdmi6TFhdKAY6ktUyY"
    NLU_URL='https://apikey-v2-yz8ut2q5yrvryc6zbtf7reuqm3ipkj2ul3tuy5yb23l:38032cd4ca78af7bc552eb9f07a9c0f9@41165407-fde5-4d7f-9595-a7ccd5c0c021-bluemix.cloudantnosqldb.appdomain.cloud'
    params = json.dumps({"text": dealerreview, "features": {"sentiment": {}}})
    response = requests.post(NLU_URL,data=params,headers={'Content-Type':'application/json'},auth=HTTPBasicAuth("apikey", API_KEY))
    
    #print(response.json())
    try:
        sentiment=response.json()['sentiment']['document']['label']
        return sentiment
    except:
        return "neutral"
