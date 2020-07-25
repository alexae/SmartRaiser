#Bibliotheken einbinden
from flask import Flask, jsonify, request
import shelve
import time
import datetime
import json
import RPi.GPIO as GPIO
from MCP3008 import MCP3008   #SPI_API

#GPIO Modus (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#GPIO Pins zuweisen
#Echo Komunikation
GPIO_TRIGGER = 3
GPIO_ECHO = 4
#Richtung der GPIO-Pins festlegen (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
#Batterie Ladestand
GPIO.setup(17, GPIO.IN) #Batterie tief
GPIO.setup(27, GPIO.IN) #Batterie 50%
GPIO.setup(22, GPIO.IN) #Batterie Ok
# Pumpe
GPIO.setup(21, GPIO.OUT) #Ansteuerung des MOSFET für den Motor

app = Flask(__name__)



    
@app.route('/')
def index():
    watering()
    return 'SmartRaiser läuft'


@app.route('/humidity', methods=['GET'])
def handle_humidity(humidity='100'):
    # Read current humidity from sensor
    adc = MCP3008()
    value = adc.read( channel = 1 ) # Den auszulesenden Channel kannst du natürlich anpassen
    humidity=value / 1023.0 * 3.3
    return jsonify(
        humidity
    ), humidity

@app.route('/waterlevel', methods=['GET'])
def handle_waterlevel():
    # Read current water level from sensor
    # setze Trigger auf HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # setze Trigger nach 0.01ms aus LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartZeit = time.time()
    StopZeit = time.time()

    # speichere Startzeit
    while GPIO.input(GPIO_ECHO) == 0:
        StartZeit = time.time()

    # speichere Ankunftszeit
    while GPIO.input(GPIO_ECHO) == 1:
        StopZeit = time.time()

    # Zeit Differenz zwischen Start und Ankunft
    TimeElapsed = StopZeit - StartZeit
    # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
    # und durch 2 teilen, da hin und zurueck
    distanz = (TimeElapsed * 34300) / 2
    return jsonify(
        waterlevel=distanz
    ), distanz
   
@app.route('/chargelevel', methods=['GET'])
def handle_chargelevel():
    # Read current charge level from sensor
    if GPIO.input(17) == GPIO.HIGH:
        chargelevel=0
    if GPIO.input(27) == GPIO.HIGH:
        chargelevel=50
    if GPIO.input(22) == GPIO.HIGH:
        chargelevel=100
    return jsonify(
        chargelevel
    )


@app.route('/humiditytoachieve', methods=['GET', 'PUT'])
def handle_humidity_to_achieve(humidity='42'):
    if request.method == 'PUT':
        content = request.json
        humidity = content['humidity']

        data = shelve.open('humidity')
        data['humidity'] = humidity
        data.close()

        return jsonify({"humidity": humidity})

    elif request.method == 'GET':
        data = shelve.open('humidity')

        if 'humidity' in data:
            return jsonify(
                humidity=data['humidity']
            ), humidity
        else:
            return "", 204

        data.close()


@app.route('/wateringtimes', methods=['GET', 'PUT'])
def handle_wateringtimes():
    if request.method == 'PUT':
        content = request.json
        wateringtimes = content['wateringtimes']

        data = shelve.open('wateringtimes')
        data['wateringtimes'] = wateringtimes
        data.close()

        return jsonify({
            "wateringtimes": wateringtimes
        })

    elif request.method == 'GET':

        data = shelve.open('wateringtimes')

        if 'wateringtimes' in data:
            print(data['wateringtimes'])
            return jsonify(
                wateringtimes=data['wateringtimes']
            )
            json.loads(wateringtimes) , wateringtimes
        else:
            return "", 204

        data.close()
def watering():
    #Bestimmen der Statischen Parameter
    #Waeserungsdauer und Messdauer in Min
    wateringduration = 3
    messuringtime = 5
    waterlevel_min = 5.0
    #Umrechnung in Minuten in ms    !!!! Zu Testzwecken auskommentiert, sonst dauert das zu lange! ;) !!!!!!
    wateringduration_in_ms = wateringduration # * 60 *1000
    messuringtime_in_ms = messuringtime # * 60 * 1000

    #Auslesen der aktuellen Feuchtigkeit und des Wasertankstands
    HA  = handle_humidity()
    HAi = int(HA[1])
    WTL = handle_waterlevel()
    
    #Auslesen der aktuellen Zeit
    timenow =(datetime.datetime.now().strftime("%H:%M"))

    #Auslesen der Feuchtigkeit welche erreicht werden soll
    data = shelve.open('humidity')
    if 'humidity' in data:
        HS=data['humidity']
        data.close()
    wateringtoachieve = int(HS['humidity'])
    #Auslesen der Bewässerungszeit
    data = shelve.open('wateringtimes')
    if 'wateringtimes' in data:
        WT=data['wateringtimes']
        data.close()
    wateringfrom = (WT['from'])
    wateringto = (WT['to'])

    #Bewässerungslogik
    if timenow >= wateringfrom and timenow <= wateringto and waterlevel_min < WTL[1] and wateringtoachieve >= HAi:

        for i in range(wateringduration_in_ms):
            GPIO.output(21, GPIO.HIGH)
            time.sleep(0.001)
            print("Bewässerung läuft")
        for i in range(messuringtime_in_ms):
            GPIO.output(21, GPIO.LOW)
            time.sleep(0.001)
            print("Messung läuft")
            
    else:
        print("Bewässerung nicht möglich")
        print(timenow)
        

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
    
