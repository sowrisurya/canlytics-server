import cantools, os
from mongoengine import GridFSProxy
from models import Vehicle
from io import StringIO

class DBCDecoder:
	def __init__(self, file_path = None, file = None):
		if isinstance(file_path, str) and file_path.endswith(".dbc") and os.path.exists(file_path):
			self.__dbc = cantools.db.load_file(file_path)
		elif isinstance(file, GridFSProxy):
			file_textio = file.read()
			file_textio = StringIO(file_textio.decode("utf-8"))
			self.__dbc = cantools.db.load(file_textio)
		elif isinstance(file, StringIO):
			self.__dbc = cantools.db.load(file)
		else:
			raise Exception("Invalid file path or file object")

	def decode_message(self, message_id: str, data: bytes):
		return self.__dbc.decode_message(message_id, data)

	def get_message(self, message_id: str):
		try:
			return self.__dbc.get_message_by_frame_id(message_id)
		except Exception as e:
			print(e)
			return None

	def get_frame_signals(self, message_id):
		message = self.get_message(message_id)
		if not message:
			return None
		return [
			{
				"name": signal.name,
				"start": signal.start,
				"length": signal.length,
				# "factor": signal.factor,
				"offset": signal.offset,
				"unit": signal.unit,
				"type": signal.is_signed and "signed" or "unsigned",
				"byte_order": signal.byte_order,
				"min": signal.minimum,
				"max": signal.maximum,
				"receivers": signal.receivers,
				"comment": signal.comment,
				# "mode": signal.mode,
			}
			for signal in message.signals
		]

	def get_frame_data(self, message_id, include_signals = False):
		message = self.get_message(message_id)
		if not message:
			return None
		return {
			"frame_id": message.frame_id,
			"name": message.name,
			# "dlc": message.dlc,
			"autosar": message.autosar,
			"prtocol": message.protocol,
			"signals": include_signals and self.get_frame_signals(message_id) or None,
		}

	def get_all_frame_ids(self, include_signals = False):
		return [
			self.get_frame_data(message.frame_id, include_signals = include_signals)
			for message in self.__dbc.messages
		]

class DBCController:
	@staticmethod
	def get_frame_ids(vehcile_id):
		vehicle = Vehicle.objects(vehicle_id = vehcile_id).first()
		if vehicle:
			dbc_decoder = DBCDecoder(file = vehicle.dbc_file.file)
			return dbc_decoder.get_all_frame_ids()
		return None

	@staticmethod
	def get_frame_signals(vehicle_id, frame_id):
		vehicle = Vehicle.objects(vehicle_id = vehicle_id).first()
		if vehicle:
			dbc_decoder = DBCDecoder(file = vehicle.dbc_file.file)
			return dbc_decoder.get_frame_signals(message_id = frame_id)
		return None

	@staticmethod
	def get_frame_data(vehicle_id, frame_id):
		vehicle = Vehicle.objects(vehicle_id = vehicle_id).first()
		if vehicle:
			dbc_decoder = DBCDecoder(file = vehicle.dbc_file.file)
			return dbc_decoder.get_frame_data(message_id = frame_id, include_signals=True)
		return None