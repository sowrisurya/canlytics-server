import mongoengine
from models.filesModel import FileFields
from bson import DBRef, ObjectId

class SelectedDIDVehicle(mongoengine.EmbeddedDocument):
	diag_name = mongoengine.StringField(required = True)
	frame_id = mongoengine.StringField(required = True)
	# frame_id = mongoengine.IntField(required = True)
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
class VehicleMake(mongoengine.DynamicDocument):
	meta = {"collection": "makes"}

class VehicleModel(mongoengine.DynamicDocument):
	meta = {"collection": "models"}

class Vehicle(mongoengine.DynamicDocument):
	vin = mongoengine.StringField(required = True, unique = True)
	model = mongoengine.ReferenceField(VehicleModel, required = True)
	make = mongoengine.ReferenceField(VehicleMake, required = True)
	meta = {"collection": "vehicles"}

class GPSCoord(mongoengine.EmbeddedDocument):
	lat = mongoengine.FloatField(required = True)
	lng = mongoengine.FloatField(required = True)
	requested_at = mongoengine.DateTimeField(required = True)

class VehicleDBCDids(mongoengine.Document):
	vehicle = mongoengine.ReferenceField(Vehicle, required = True)
	model = mongoengine.ReferenceField(VehicleModel, required = True)
	device_id = mongoengine.StringField(required = True, unique = True)
	# dbc_file = mongoengine.EmbeddedDocumentField(FileFields)
	dids_list = mongoengine.EmbeddedDocumentListField(SelectedDIDVehicle)
	gps = mongoengine.EmbeddedDocumentField(GPSCoord)
	current_status = mongoengine.StringField(default = "off")
	# vin_decode = mongoengine.EmbeddedDocumentField(SelectedDIDVehicle)
