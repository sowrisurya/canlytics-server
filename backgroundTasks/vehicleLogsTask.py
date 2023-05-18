from models import VehicleDBCDids
from subscribers import StatusGetter
from backgroundTasks.celery_app import celery_app
import time, asyncio, json
from utils import REDIS_CLIENT, Logger
from subscribers.vehicleLogsSubscriber import VehicleLogsSubscriber
import functools

logger = Logger(__name__)
# from controller.

def wait_for_data(callback, timeout = 30):
	subscriber = REDIS_CLIENT.pubsub()
	subscriber.subscribe("dataAdderSubscribe")

	st = time.time()
	while time.time() - st < timeout:
		msg = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)
		if msg:
			data = json.loads(msg["data"].decode("utf-8"))
			try:
				callback(data["crnt_msg"], data["data"])
			except Exception as e:
				logger.error(f"Error running {callback}. {e}")
		else:
			time.sleep(1)

async def wait_for_data_async(callback, timeout = 15, async_event: asyncio.Event = None):
	subscriber = REDIS_CLIENT.pubsub()
	subscriber.subscribe("dataAdderSubscribe")

	st = time.time()
	while time.time() - st < timeout:
		msg = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)
		if msg:
			data = json.loads(msg["data"].decode("utf-8"))
			try:
				callback(data["crnt_msg"], data["data"])
			except Exception as e:
				logger.error(f"Error running {callback}. {e}")
		else:
			await asyncio.sleep(1)
	if async_event:
		async_event.set()

def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))
    return wrapper

@celery_app.task(name = "backgroundTasks.vehicle_logs_schedule")
def vehicle_logs_schedule():
	logger.info("vehicle_logs_schedule started")

	for vehicle_dbc in VehicleDBCDids.objects():
		logs_controller = VehicleLogsSubscriber(
			vehicle_ids = [vehicle_dbc.vehicle.vin],
			dids_list = vehicle_dbc.dids_list,
			timeout = 10
		)
		loop = asyncio.get_event_loop()
		logs = loop.run_until_complete(logs_controller.get_logs())

	return True


# @celery_app.task(name = "backgroundTasks.gps_status_schedule")
# @sync
async def gps_status_schedule():
	print("gps_status_schedule")
	logger.info("gps_status_schedule started")

	def callback(data: str):
		data = data.lower()
		if data.startswith("server:"):
			return
		print("callback", data)
		StatusGetter.status_diagonostic_callback(data = data)
		log_subscriber.set_crnt_msg()

	log_subscriber = VehicleLogsSubscriber(
		vehicle_ids = [],
		dids_list = [],
		add_to_influx = False,
		callback = callback,
		timeout = 10
	)

	for vehicle_dbc in VehicleDBCDids.objects():
		log_subscriber.publish_raw(device_id = vehicle_dbc.device_id, message = "Fetch GPS")
		await log_subscriber.wait_for_msgs_recvd()
		# loop.run_until_complete(log_subscriber.wait_for_msgs_recvd())
		log_subscriber.publish_raw(device_id = vehicle_dbc.device_id, message = "Vehicle Status")
		await log_subscriber.wait_for_msgs_recvd()

	# StatusGetter.publish_gps()
	# StatusGetter.publish_vehicle_status()


	# wait_for_data(callback=StatusGetter.status_diagonostic_callback, timeout=20)

	logger.info("done")
	return True