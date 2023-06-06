from typing import List
from pprint import pprint
from copy import deepcopy
import time
from io import StringIO

### Read the config file and parse
def readConfigFile(configFile):
	with open(configFile, 'r') as f:
		config = f.readlines()
	return config

def parseConfigFile(config: List[str]):
	meta_info = {}
	nodes = []

	node_started = False
	total_lines = len(config)
	start_line = 0
	current_node = []
	did_data = {}
	ecu_network_data = {}

	while start_line < total_lines:
		line = config[start_line]
		line = line.replace("\r", "")
		if line.startswith("//"):
			start_line += 1
			continue
		if line.startswith("node"):
			node_started = True
			start_line += 1
			continue
		if node_started:
			if line.startswith("{"):
				start_line += 1
				continue
			elif line.startswith("}"):
				node_started = False
				start_line += 1
				if len(did_data) != 0:
					current_node.append(deepcopy(did_data))
				nodes.append({
					"ecu_network_info": deepcopy(ecu_network_data),
					"nodes": deepcopy(current_node)
				})
				current_node = []
				did_data = {}
				continue
			elif line.startswith("\t\n") or line.startswith("\n") or (line.startswith("\t") and len(line) == 1):
				if len(did_data) != 0:
					current_node.append(deepcopy(did_data))
				did_data = {}
				start_line += 1
				continue
			elif line.startswith("\t") or line.startswith("    "):
				if " = " in line or "\t= " in line or " =\t" in line or "\t=\t" in line:
					param, info = line.split(" = ") if " = " in line else (
						line.split("\t= ") if "\t= " in line else (
							line.split(" =\t") if " =\t" in line else line.split("\t=\t")
						)
					)
					if "ecu_network" in param:
						ecu_network_data["network"] = info.strip().rstrip(";").strip("\n").strip("\"")
					elif "ecu_address" in param:
						ecu_network_data["address"] = info.strip().rstrip(";").strip("\n").strip("\"").replace("0x", "")
					elif "ecu_name" in param:
						ecu_network_data["name"] = info.strip().rstrip(";").strip("\n").strip("\"")
					elif "ecu_info" in param:
						ecu_network_data["info"] = info.strip().rstrip(";").strip("\n").strip("\"")
					elif "ecu_delay" in param:
						ecu_network_data["delay"] = info.strip().rstrip(";").strip("\n").strip("\"")

					elif "did_info" in param:
						did_data["info"] = info.strip().rstrip(";").strip("\n").strip("\"")
					elif "did_type" in param:
						did_data["type"] = info.strip().rstrip(";").strip("\n").strip("\"")
					elif "did_tag" in param:
						did_data["tag"] = info.strip().rstrip(";").strip("\n").strip("\"")
					elif "did_read" in param:
						did_data["read"] = info.strip().rstrip(";").strip("\n").strip("\"").replace("0x", "")
						if not did_data["read"].startswith("22"):
							did_data["read"] = "22 " + did_data["read"]
			elif line.startswith("\n"):
				start_line += 1
				continue
		else:
			if line.startswith("\n"):
				start_line += 1
				continue
			if len(line) != 0 and not line.startswith("\r\n") and not line.startswith("\n"):
				meta_info[line.split("=")[0].strip()] = line.split("=")[1].strip().rstrip(";").strip("\"")
		start_line += 1

	return meta_info, nodes

def readParseConfigFile(configFilePath: str = None, configFile: StringIO = None):
	if configFilePath is not None:
		config = readConfigFile(configFilePath)
	elif configFile is not None:
		config = configFile.readlines()
	else:
		raise Exception("Either configFilePath or configFile should be provided")
	return parseConfigFile(config)

if __name__ == "__main__":
	st = time.perf_counter()
	config = readConfigFile("SS5_MLA_24MY.cfg")
	meta_info, ecu_nodes = parseConfigFile(config)
	print(f"Time taken: {time.perf_counter() - st}")
	pprint(meta_info)
	pprint(ecu_nodes)