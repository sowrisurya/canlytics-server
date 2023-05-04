import mongoengine

class FileFields(mongoengine.EmbeddedDocument):
	file = mongoengine.FileField(required = True)
	name = mongoengine.StringField(required = True)
	content_type = mongoengine.StringField()
	size = mongoengine.IntField(default = 0)