from influxdb import InfluxDBClient
from utils.consts import (
	INFLUX_HOST,
	INFLUX_PORT,
	INFLUX_USER,
	INFLUX_PASSWORD,
	INFLUX_DBNAME
)
import datetime

class InfluxClient:
	def __init__(self, host = INFLUX_HOST, port = INFLUX_PORT, user = INFLUX_USER, password = INFLUX_PASSWORD, dbname = INFLUX_DBNAME):
		self.__client = InfluxDBClient(host, port, user, password, dbname)

	def write(self, measurement, tags, fields):
		json_body = [
			{
				"measurement": measurement,
				"tags": tags,
				"time": datetime.datetime.utcnow().isoformat(),
				"fields": fields,
			}
		]
		self.__client.write_points(json_body)

	def query(self, query):
		return self.__client.query(query)