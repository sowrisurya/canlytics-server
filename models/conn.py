import mongoengine
import urllib.parse
from utils.consts import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    DB_AUTH_DATABASE
)

if DB_USER and DB_PASSWORD and DB_AUTH_DATABASE:
	MONGO_CONN = f"mongodb://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource={DB_AUTH_DATABASE}"
else:
	MONGO_CONN = f"mongodb://{DB_HOST}:{DB_PORT}/{DB_NAME}"

mongoengine.connect(host = MONGO_CONN)