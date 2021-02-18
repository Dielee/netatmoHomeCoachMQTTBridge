# netatmoHomeCoachMQTTBridge
Provides data from netatmo home coach via MQTT, using pyatmo and phao mqtt.

Please use Pyton 3.x and install the following dependencies:

> pip3 install pyatmo, paho-mqtt
> 

After installing the dependencies, fill in your data from netatmo and an MQTT broker in config.yaml. 

**Updateinterval is now fixed.**

Data is fetched every five minutes from last netatmo publishing time.
