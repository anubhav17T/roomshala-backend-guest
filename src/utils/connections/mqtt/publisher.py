import json
from src.utils.connections.mqtt.connection import MqttClient
from src.utils.logger.logger import logger


class Publisher(object):
    def __init__(self, userId, experimentId, topic):
        self.mqtt = MqttClient().clientMqtt()
        self.userId = userId
        self.experimentId = experimentId
        self.topic = topic

    def states(self, state: str):
        logger.info("############ SENDING DATA TO MQTT FOR STATES #############")
        payload = {"userId": self.userId, "experimentId": self.experimentId,
                   "status": state}
        payloadSplitInProcess = json.dumps(payload)
        logger.info("########## PUBLISHING STATE DATA ON MQTT ###############")
        self.mqtt.publish(topic=self.topic, payload=payloadSplitInProcess,
                          qos=0)
        logger.info("########## SUCCESS IN PUBLISHING STATE ################")

    def data(self, payload):
        logger.info("############ SENDING DATA TO MQTT FOR MODEL DETAILS #############")
        payload_to_sent = {"userId": self.userId, "experimentId": self.experimentId,
                           "status": payload}
        payload_to_sent = json.dumps(payload_to_sent)
        logger.info("############ DUMPING COMPLETE #############")
        self.mqtt.publish(topic=self.topic, payload=payload_to_sent,
                          qos=0)