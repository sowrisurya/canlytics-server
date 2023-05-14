from subscribers import DataAdderQueue
import asyncio

async def main():
	DATA_ADDER_QUEUE = DataAdderQueue()
	loop = asyncio.get_event_loop()
	task = loop.create_task(DATA_ADDER_QUEUE.configure())
	await DATA_ADDER_QUEUE.wait_for_messages_async()
	# task = loop.create_task(DATA_ADDER_QUEUE.wait_for_messages_async())
	# print("Waiting for messages")
	# DATA_ADDER_QUEUE.configure()

if __name__ == "__main__":
	asyncio.run(main())	
	# asyncio.run(DATA_ADDER_QUEUE.wait_for_messages())
	# DATA_ADDER_QUEUE.wait_for_messages()