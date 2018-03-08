from flask import Flask, request
import requests
import json
import twilio
import twilio.rest
import unicodedata 
from twilio.rest import TwilioRestClient
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from yelp.config import SEARCH_PATH
from yelp.obj.search_response import SearchResponse
from pprint import pprint




app = Flask(__name__)
        
@app.route('/messages', methods=['GET', 'POST'])
def show_messages():
    api = 'https://api.twilio.com/2010-04-01'
    uri = '/Accounts/' + ACCOUNT_SID + '/Messages.json'
    credentials = (ACCOUNT_SID, AUTH_TOKEN)
    response = requests.get(api + uri, auth=credentials)
    messages = json.loads(response.content)
    pprint(messages)
    return str(messages)
    
def _send_sms_notification(to, message_body, callback_url):
    account_sid = app.config['TWILIO_ACCOUNT_SID']
    auth_token = app.config['TWILIO_AUTH_TOKEN']
    twilio_number = app.config['TWILIO_NUMBER']
    client = TwilioRestClient(account_sid, auth_token)
    client.messages.create(to=to,
                           from_=twilio_number,
                           body=message_body,
                           status_callback=callback_url)

auth = Oauth1Authenticator(
    consumer_key="k9mKvERv6YI6Le3OGwH8iw",
    consumer_secret="o-bZL86Y68L9hCTBnD34o9bHYUg",
    token="RfV2-OIlXCuK3-iFFJ8sHs5kMLcV4iOG",
    token_secret="eO4YfPOZhHYjtDuZxFSld81APQ0"
)

client = Client(auth)

limit = 3


@app.route('/yelp', methods=['GET'])
def get_search_parameters():
    
    input = request.values.get('Body')
    input_array = input.split(',')
    
#See the Yelp API for more details
    params = {
        'limit': limit,
        'term': input_array[0],
        'location': input_array[1],
        
    }

    yelp_results = client.search(**params)
    
    
    return_yelp_results = []
    

    for x in range(limit):
        address = yelp_results.businesses[x].location.display_address
        return_yelp_results.append(str(yelp_results.businesses[x].name))
        return_yelp_results.append("Rating:" + str(yelp_results.businesses[x].rating))
        return_yelp_results.append(", ".join(address))
        return_yelp_results.append(str(yelp_results.businesses[x].display_phone))
        return_yelp_results.append(str(yelp_results.businesses[x].mobile_url))
        return_yelp_results.append("\n")
       
  
    return_yelp_results

    message = "Here is what I found for you!\n\n" + "\n".join(return_yelp_results)

    resp = twilio.twiml.Response()
    resp.sms(message)
 
    return str(resp)

   
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
