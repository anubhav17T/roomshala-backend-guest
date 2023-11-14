import time
from src.utils.logger.logger import logger
from src.constants.properties import KEYS
import time
import paho.mqtt.client as mqtt


class MqttClient:
    try:
        def __init__(self):
            try:
                self.client = mqtt.Client()
                self.client.username_pw_set(username=KEYS["MQTT_USERNAME"],
                                            password=KEYS["MQTT_PASSWORD"])  # create new instance
                logger.info("################ mqtt broker called ###################################  ")

            except Exception as e:
                logger.info("######## SOMETHING IS WRONG WITH MQTT USERNAME OR PASSWORD ##### {}".format(e))

        def clientMqtt(self):
            self.client.connect(host=KEYS["MQTT_HOST"], port=KEYS["MQTT_PORT"],
                                keepalive=KEYS["MQTT_KEEPALIVE"])  # connect to broker
            self.client.loop_start()  # start the loop
            time.sleep(4)  # wait
            self.client.loop_stop()
            return self.client  # start

    except Exception as e:
        logger.error("################ Something is wrong with mqtt publisher################ {}".format(e))
