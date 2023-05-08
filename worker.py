from subscribers import DataAdderQueue
import asyncio

if __name__ == "__main__":
	DATA_ADDER_QUEUE = DataAdderQueue()
	thrd = DATA_ADDER_QUEUE.configure()
	DATA_ADDER_QUEUE.wait_for_messages()
	# asyncio.run(DATA_ADDER_QUEUE.wait_for_messages())
	# DATA_ADDER_QUEUE.wait_for_messages()