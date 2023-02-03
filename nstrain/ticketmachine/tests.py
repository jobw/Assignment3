from django.test import TestCase, Client
import requests
#from views import getprice, gettrips

def client_get_planning(client, from_station, to_station, travel_class, way, passengers):
    response = client.get("/planning",{'from_station' : from_station 
                    ,"to_station" : to_station 
                    , "travel_class" : travel_class
                    , "way" : way
                    , "passengers": passengers })
    return response
    

class TicketTestCase(TestCase):

    # ADD YOUR TEST FUNCTIONS HERE
    def test_server_failure(self):
        c = Client()
        url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/price"
        params = {}
        headers = {'Ocp-Apim-Subscription-Key': '06f223dd2fbc41389afc332c14d17447'}
        response = requests.get(url=url, params=params ,headers=headers)
        response_planning = client_get_planning(c,"UT","AMF","2","return","5")
        if(response.status_code == 404):
            self.assertAlmostEqual(response_planning['price'],"Failed to connect to the price server")
        else : 
            self.assertEqual(response.status_code,200)

    def test_multiple_first_class_tickets(self):
        c = Client()
        response = client_get_planning(c,"UT","AMF","1","return","5")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['price'],90.1)


    def test_ticket_to_own_station(self):
        c = Client()
        response = client_get_planning(c,"UT","UT","1","return","1")
        self.assertEqual(response.context['price'], "The stations you chose don't result in a valid trip")


    def test_index(self):
        c = Client()
        # Set up client to make requests

        # Send get request to index page and store response
        response = c.get("/ticketmachine")

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)
