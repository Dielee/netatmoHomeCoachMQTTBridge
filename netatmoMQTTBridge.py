import pyatmo
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import datetime
import time
from datetime import timedelta  
import yaml


def main():

    # Load cfg
    cfg = loadConf()
    
    # Initial Update on startup
    airData = getNetatmoData(cfg)
    sendToHA(airData, cfg)
    nextFetchSec = getNextFetchTime (airData['lastUpdate'][0])
    
    while True:
        time.sleep(nextFetchSec)
        airData = getNetatmoData(cfg)
        sendToHA(airData, cfg)
        nextFetchSec = getNextFetchTime (airData['lastUpdate'][0])

        
def getNextFetchTime (lastUpdate):
    
    now = datetime.datetime.today()
    logToConsole (f"Last update from Netatmo was {lastUpdate}")

    nextFetch = lastUpdate + timedelta(minutes=5, seconds=15)
    if (nextFetch < now):
        nextFetch = nextFetch + timedelta(minutes=5)
    
    nextFetchSec = (nextFetch - now).seconds

    logToConsole (f"Wait for {nextFetchSec} seconds until next fetch at {nextFetch}...")

    return nextFetchSec


def getNetatmoData (cfg):
    
    authorization = pyatmo.ClientAuth(
    client_id= cfg['netatmoMQTTBridge']['CLIENT_ID'],
    client_secret=cfg['netatmoMQTTBridge']['CLIENT_SECRET'],
    username=cfg['netatmoMQTTBridge']['USERNAME'],
    password=cfg['netatmoMQTTBridge']['PASSWORD'],
    scope="read_homecoach",
    )

    airData = pyatmo.HomeCoachData(authorization)

    logToConsole ("Fetching data from Netatmo cloud...")

    MACADRESS = cfg['netatmoMQTTBridge']['MACADRESS']
    raw = airData.raw_data
    data = airData.get_last_data(MACADRESS)

    airData = {}

    airData['lastUpdate'] = datetime.datetime.fromtimestamp(data[MACADRESS]['When']), "mdi:timer", ""
    airData['Temperature'] = data[MACADRESS]['Temperature'], "mdi:thermometer", "°C"
    airData['Humidity'] = data[MACADRESS]['Humidity'], "hass:water-percent", "%"
    airData['CO2'] = data[MACADRESS]['CO2'], "mdi:molecule-co2", "ppm"
    airData['Noise'] = data[MACADRESS]['Noise'], "mdi:volume-high", "dB"
    airData['Pressure'] = data[MACADRESS]['Pressure'], "hass:gauge", "mbar"
    airData['AbsolutePressure'] = data[MACADRESS]['AbsolutePressure'], "hass:gauge", "mbar"
    airData['Health_idx'] = getHealthIdx(data[MACADRESS]['health_idx']), "mdi:cloud", ""
    airData['Reachable'] = data[MACADRESS]['reachable'], "mdi:wifi", ""
    airData['WifiStatus'] = getWifiStatus(data[MACADRESS]['wifi_status']), "mdi:wifi", ""
    airData['CO2Calibrating'] = raw[0]['co2_calibrating'], "mdi:ab-testing", ""

    return airData

def sendToHA (airData, cfg):
    for key, value in airData.items():

        mqttBrokerIP = cfg['netatmoMQTTBridge']['mqttBrokerIP']

        payload = {}
        payload['name'] = f"netatmoMQTTBridge - {key}"
        payload['icon'] = value[1]
        payload['state_topic'] = f"homeassistant/sensor/netatmoMQTTBridge_{key}/state"
        payload['unit_of_measurement'] = value[2]
        payload['unique_id'] = f"netatmoMQTTBridge_{key}"

        jsonParams = json.dumps(payload)

        publish.single(f"homeassistant/sensor/netatmoMQTTBridge_{key}/config", 
                        payload=jsonParams, qos=0, retain=False, hostname=mqttBrokerIP,
                        port=1883, client_id="netatmoMQTTBridge", keepalive=60, will=None, 
                        tls=None, protocol=mqtt.MQTTv311, transport="tcp")

        if (isinstance(value[0], datetime.datetime)):
            payload = value[0].strftime('%H:%M %d.%m.%Y')
        else:
            payload = value[0]

        publish.single(f"homeassistant/sensor/netatmoMQTTBridge_{key}/state", 
                payload=payload, qos=0, retain=False, hostname=mqttBrokerIP,
                port=1883, client_id="netatmoMQTTBridge", keepalive=60, will=None, 
                tls=None, protocol=mqtt.MQTTv311, transport="tcp")

def logToConsole (text):
    now = datetime.datetime.today()
    print (f"{now} - {text}")

def getWifiStatus (wifi_status):
    if (wifi_status <= 56):
        wifi_status = "Good"
    elif (wifi_status >= 57 and wifi_status <= 71):
        wifi_status = "Average"
    elif (wifi_status >= 72):
        wifi_status = "Bad"

    return wifi_status

def getHealthIdx (health_idx):
    if (health_idx == 0):
        health_idx = "Healthy"
    elif (health_idx == 1):
        health_idx = "Fine"
    elif (health_idx == 2):
        health_idx = "Fair"
    elif (health_idx == 3):
        health_idx = "Poor"
    elif (health_idx == 4):
        health_idx = "Unhealthy"

    return health_idx

def loadConf ():
    with open("config.yaml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg

main()