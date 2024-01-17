# from src.constants.properties import KEYS
# from src.utils.logger.logger import logger
# # import consul
#
#
# def connection_service(host, port):
#     if host[-1] == ":":
#         host = host[:-1]
#     logger.info("======== HOST {} AND PORT IS {} ==============".format(host, port))
#     try:
#         connection = consul.Consul(host=host, port=port)
#     except TimeoutError as e:
#         logger.error("============= TIMEOUT CONNECTION ERROR {} ==================".format(e))
#         return False
#     for info in KEYS.keys():
#         # index, key = connection.kv.get('config/backend/' + info)
#         index, key = connection.kv.get('config/app-face-recog/' + info)
#         KEYS[info] = key['Value'].decode('utf-8')
#     if not KEYS:
#         logger.error("============== NONE TYPE KEYS INFORMATION ================")
#         return False
#     logger.info("===== SUCCESSFULLY FETCHED KEYS AND INFORMATION====")
#     logger.info("====== KEYS INFORMATION IS {}====".format(KEYS))
#     return KEYS