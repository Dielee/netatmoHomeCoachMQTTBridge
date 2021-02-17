# netatmoHomeCoachMQTTBridge
Provides data from netatmo home coach via MQTT, using pyatmo and phao mqtt.

Please use Pyton 3.x and install the following dependencies:

> pip3 install pyatmo, paho-mqtt
> 

After installing the dependencies, fill in your data from netatmo and an MQTT broker. 

The interval of data collection is freely selectable. 
Every time the script starts, data is fetched.

**More often than every 5 minutes should not be set.**
