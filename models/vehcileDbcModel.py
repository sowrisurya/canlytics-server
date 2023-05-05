import mongoengine
from models.filesModel import FileFields
from bson import DBRef, ObjectId

class SelectedDIDVehicle(mongoengine.EmbeddedDocument):
	diag_name = mongoengine.StringField(required = True)
	frame_id = mongoengine.IntField(required = True)
	start_bit = mongoengine.IntField(required = True)
	hex_data = mongoengine.StringField()
	# did = mongoengine.StringField()

# class Vehicle(mongoengine.Document):
# 	vehicle_id = mongoengine.StringField(required = True, unique = True)
# 	vehicle_name = mongoengine.StringField(required = True)
# 	vehicle_type = mongoengine.StringField(required = True)
# 	vehicle_model = mongoengine.StringField(required = True)
# 	vehicle_make = mongoengine.StringField(required = True)
# 	chip_id = mongoengine.StringField(required = True)
# 	vehicle_status = mongoengine.BooleanField(default = False)
# 	dbc_file = mongoengine.EmbeddedDocumentField(FileFields)
# 	dids_list = mongoengine.EmbeddedDocumentListField(SelectedDIDVehicle)
class VehicleModel(mongoengine.DynamicDocument):
	meta = {"collection": "models"}

class Vehicle(mongoengine.DynamicDocument):
	model = mongoengine.ReferenceField(VehicleModel, required = True)
	meta = {"collection": "vehicles"}

class VehicleDBCDids(mongoengine.Document):
	vehicle = mongoengine.ReferenceField(Vehicle, required = True)
	model = mongoengine.ReferenceField(VehicleModel, required = True)
	device_id = mongoengine.StringField(required = True, unique = True)
	# dbc_file = mongoengine.EmbeddedDocumentField(FileFields)
	dids_list = mongoengine.EmbeddedDocumentListField(SelectedDIDVehicle)
	# vin_decode = mongoengine.EmbeddedDocumentField(SelectedDIDVehicle)
