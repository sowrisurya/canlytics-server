import influxdb_client
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS
from utils.consts import (
	INFLUX_HOST,
	INFLUX_ORG,
	INFLUX_TOKEN,
	INFLUX_DBNAME
)
import datetime

class InfluxClient:
	def __init__(self, host = INFLUX_HOST, org = INFLUX_ORG, auth_token = INFLUX_TOKEN, dbname = INFLUX_DBNAME):
		# self.__client = InfluxDBClient(host, port, database = dbname)
		self.__org = org
		self.__bucket = dbname

		self.__client = influxdb_client.InfluxDBClient(
			url=host,
			token=auth_token,
			org=self.__org
		)


		self.__write_api = self.__client.write_api(write_options=SYNCHRONOUS)
		self.__read_api = self.__client.query_api()

	def write(self, measurement, tags: dict, fields: dict):
		point = influxdb_client.Point(measurement)
		# point = point.tag(**tags)
		# point = point.field(**fields)
		for key, value in tags.items():
			point.tag(key, value)
		for key, value in fields.items():
			point.field(field = key, value = value)
		point.time(datetime.datetime.utcnow())
		self.__write_api.write(bucket=self.__bucket, record=point)

	def delete_all(self):
		self.__client.delete_api().delete(
			predicate='',
			bucket=self.__bucket,
			org=self.__org,
			start=datetime.datetime(1970, 1, 1),
			stop=datetime.datetime.utcnow(),
		)

	def query(self, query):
		return self.__read_api.query(org=self.__org, query=query)
	
	def queryV1(self, query):
		return self.__read_api.query_raw(org=self.__org, query=query)

INFLUX_CLIENT = InfluxClient()