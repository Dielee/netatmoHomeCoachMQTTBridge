import pyatmo
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

CLIENT_ID = '<dev.netatmo - clientID>'
CLIENT_SECRET = '<dev.netatmo - clientSecret>'
USERNAME = '<netatmo e-mail>'
PASSWORD = '<netatmo - password>'
MACADRESS = '<homecoach macAdress>'
mqttBrokerIP = '<mqtt broker ip or fqdn>'

def main():
    airData = getNetatmoData()
    sendToHA(airData)


def getNetatmoData ():
    authorization = pyatmo.ClientAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD,
    scope="read_homecoach",
    )

    airData = pyatmo.HomeCoachData(authorization)

    raw = airData.raw_data
    data = airData.get_last_data(MACADRESS)

    airData = {}

    airData['Temperature'] = data[MACADRESS]['Temperature'], "mdi:thermometer", "°C"
    airData['Humidity'] = data[MACADRESS]['Humidity'], "hass:water-percent", "%"
    airData['CO2'] = data[MACADRESS]['CO2'], "mdi:molecule-co2", "ppm"
    airData['Noise'] = data[MACADRESS]['Noise'], "mdi:volume-high", "dB"
    airData['Pressure'] = data[MACADRESS]['Pressure'], "hass:gauge", "mbar"
    airData['AbsolutePressure'] = data[MACADRESS]['AbsolutePressure'], "hass:gauge", "mbar"
    airData['Health_idx'] = data[MACADRESS]['health_idx'], "mdi:cloud", ""
    airData['Reachable'] = data[MACADRESS]['reachable'], "mdi:wifi", ""
    airData['WifiStatus'] = data[MACADRESS]['wifi_status'], "mdi:wifi", ""
    airData['CO2Calibrating'] = raw[0]['co2_calibrating'], "mdi:ab-testing", ""

    return airData

def sendToHA (airData):
    for key, value in airData.items():

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

        publish.single(f"homeassistant/sensor/netatmoMQTTBridge_{key}/state", 
                payload=value[0], qos=0, retain=False, hostname=mqttBrokerIP,
                port=1883, client_id="netatmoMQTTBridge", keepalive=60, will=None, 
                tls=None, protocol=mqtt.MQTTv311, transport="tcp")

    
main()