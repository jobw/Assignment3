from django.shortcuts import render
from django import forms
import requests

# (STATION UIcCODE, STATION NAME)
stations = (
    ("UT", "Utrecht Centraal"),
    ("GVC", "Den Haag Centraal"),
    ("RTD", "Rotterdam Centraal"),
    ("ASD", "Amsterdam Centraal"),
    ("EHV", "Eindhoven Centraal"),
    ("GN", "Groningen"),
    ("TB", "Tilburg"),
    ("AMF", "Amersfoort Centraal"),
    ("AH", "Arnhem Centraal"),
    ("LEDN", "Leiden Centraal"),
    ("NM", "Nijmegen"),
    ("BD", "Breda"),
    ("DT", "Delft"),
    ("HLM", "Haarlem")
)

travel_class = (
    ('1', 'First class'),
    ('2', 'Second class'),
)

ways = (('single', 'One way'),
       ('return', 'Return')
       )

payment_methods = (('1', 'Debit Card'),
                   ('2', 'Credit Card'),
                   ('3', 'Cash')
                   )

headers = {'Ocp-Apim-Subscription-Key': '06f223dd2fbc41389afc332c14d17447'}

# make a form for ticket
class SelectTicketForm(forms.Form):
    from_station = forms.ChoiceField(choices=stations)
    to_station = forms.ChoiceField(choices=stations)
    travel_class = forms.CharField(label='Travel class', widget=forms.RadioSelect(choices=travel_class))
    way = forms.CharField(label='Way', widget=forms.RadioSelect(choices=ways))
    passengers = forms.IntegerField(label="Number of passengers", min_value=1, max_value=10)


# make a form for payment methods
class PaymentForm(forms.Form):
    payment = forms.CharField(label='Payment Method', widget=forms.RadioSelect(choices=payment_methods))


def index(request):
    return render(request, "ticketmachine/index.html", {
        "form": SelectTicketForm({'travel_class': '2', 'way': 'single', 'discount': '1', 'passengers': 1})
    })


def planning(request):
    if request.method == "GET":
        gotform = SelectTicketForm(request.GET)
        return render(request, "ticketmachine/planning.html", {
            "form": PaymentForm({'payment': '2'}),
            "price": getprice(gotform['from_station'].value()
                             ,gotform['to_station'].value()
                             ,gotform['travel_class'].value()
                             ,gotform['way'].value()
                             ,gotform['passengers'].value()),
            "trips": gettrips(gotform['from_station'].value(),gotform['to_station'].value()),
        })


def payment(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form['payment'].value()
            return render(request, "ticketmachine/payment.html", {
                "payment_method": payment_method,
            })
        else:
            return render(request, "ticketmachine/planning.html", {
                "form": form,
                "price": getprice(),
                "trips": gettrips()
            })
    return render(request, "ticketmachine/planning.html", {
        "form": PaymentForm({'payment': '1'}),
    })


def gettrips(from_station, to_station):
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips"
    params = {"fromStation" : from_station,
            "toStation" : to_station}

    # SEND A PROPER REQUEST TO URL AND POPULATE "trips" WITH REQUIRED FIELDS IN THE RESPONSE OF API
    # trips = [{"final_destination": "Amsterdam Centraal", "plannedDateTime": "2023-01-18 10:48",
    #           "plannedDurationInMinutes": "38", "transfers": "2",
    #           "crowdForecast": "normal"}]
    result = requests.get(url=url, headers=headers, params=params)
    if result.status_code == 200:
        jsonResponse = result.json()
        legsvar = 0
        trips = []
        for trip in range(0, len(jsonResponse["trips"])):
            trips.append({"final_destination": jsonResponse['trips'][trip]['legs'][(len(jsonResponse['trips'][trip]['legs'])-1)]['destination']['name'], 
                          "plannedDateTime": jsonResponse['trips'][trip]['legs'][0]['origin']['plannedDateTime'],
                          "plannedDurationInMinutes": jsonResponse['trips'][trip]['plannedDurationInMinutes'], 
                          "transfers": jsonResponse['trips'][trip]['transfers'],
                          "crowdForecast": jsonResponse['trips'][trip]['crowdForecast']})
            
        return trips
    elif result.status_code == 404:
        return "Failed to connect to the information server"
    else:
        return "The stations you chose don't result in a valid trip"

def getprice(from_station, to_station, travel_class, way, tickets):
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/price"
    params = {"fromStation" : from_station,
              "toStation" : to_station,
              "travelClass" : str(travel_class),
              "travelType" : way}


    # SEND A PROPER REQUEST TO URL AND POPULATE "total_price" WITH "totalPriceInCents" FIELD IN THE RESPONSE
    print([params])


    result = requests.get(url=url, headers=headers, params=params)
    if result.status_code == 200:
        jsonResponse = result.json()
        return (jsonResponse["payload"]["totalPriceInCents"]* int(tickets)) / 100
    elif result.status_code == 404:
        return "Failed to connect to the price server"
    else:
        return "The stations you chose don't result in a valid trip"
