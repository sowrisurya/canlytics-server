from __future__ import annotations
import yaml
import os

config_file = os.environ.get("CONFIG_FILE", "data/config.yaml")
with open(config_file, "r") as f:
    CONFIG = yaml.safe_load(f)

DB_DETAILS = CONFIG["database"]
DB_NAME = DB_DETAILS["name"]
DB_USER = DB_DETAILS["user"]
DB_PASSWORD = DB_DETAILS["password"]
DB_HOST = DB_DETAILS["host"]
DB_PORT = DB_DETAILS["port"]
DB_AUTH_DATABASE = DB_DETAILS["auth_database"]

MQTT_DETAILS = CONFIG["mqtt"]
MQTT_HOST = MQTT_DETAILS["host"]
MQTT_PORT = MQTT_DETAILS["port"]
MQTT_CLIENT_ID = MQTT_DETAILS["client_id"]
MQTT_TOPIC = MQTT_DETAILS["topic"]
MQTT_IN_TOPIC = MQTT_DETAILS["in_topic"]
MQTT_OUT_TOPIC = MQTT_DETAILS["out_topic"]
MQTT_ROOT_CA = MQTT_DETAILS["root_ca"]
MQTT_PRIVATE_KEY = MQTT_DETAILS["private_key"]
MQTT_CERTIFICATE = MQTT_DETAILS["certificate"]

REDIS_DETAILS = CONFIG["redis"]
REDIS_HOST = REDIS_DETAILS["host"]
REDIS_PORT = REDIS_DETAILS["port"]
REDIS_PASSWORD = REDIS_DETAILS["password"]
REDIS_DB = REDIS_DETAILS["db"]

INFLUX_DETAILS = CONFIG["influx"]
INFLUX_HOST = INFLUX_DETAILS["host"]
INFLUX_ORG = INFLUX_DETAILS["org"]
INFLUX_TOKEN = INFLUX_DETAILS["token"]
INFLUX_DBNAME = INFLUX_DETAILS["database"]