import boto3

class IOTClient:
	def __init__(self, access_key, secret_key):
		self.__session = boto3.Session(
			aws_access_key_id = access_key,
			aws_secret_access_key = secret_key,
			region_name="eu-central-1",
		)
		self.__iot_client = self.__session.client('iot')

	def create_thing(self, thing_name):
		return self.__iot_client.create_thing(
			thingName = thing_name,
		)