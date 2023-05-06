from subscribers import DataAdderQueue

if __name__ == "__main__":
	DATA_ADDER_QUEUE = DataAdderQueue()
	DATA_ADDER_QUEUE.configure()
	DATA_ADDER_QUEUE.wait_for_messages()