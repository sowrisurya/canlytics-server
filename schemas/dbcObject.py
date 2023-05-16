from pydantic import BaseModel
from typing import Optional, List

class FrameSignal(BaseModel):
	name: str
	start: int
	length: int
	# factor: Optional[float]
	offset: int
	unit: Optional[str]
	type: str
	byte_order: Optional[str]
	min: Optional[float]
	max: Optional[float]
	receivers: Optional[List[str]]
	comment: Optional[str]
	# mode: Optional[str]

class CANFrame(BaseModel):
	frame_id: int
	name: str
	# dlc: int
	autosar: Optional[str]
	protocol: Optional[str]
	signals: Optional[List[FrameSignal]]

class ECUNetworkInfo(BaseModel):
	network: str
	address: str
	name: str
	info: str
	delay: int

class NetworkNode(BaseModel):
	read: str
	info: str
	type: int
	tag: str

class NodeLayout(BaseModel):
	nodes: Optional[List[NetworkNode]] = []
	ecu_network_info: ECUNetworkInfo

class CFGMetaInfo(BaseModel):
	config_name: str
	config_version: str
	config_vehicle: str
	config_veh_init: str
	protocol_hsc: str
	dflt_port_num: str
	dflt_port_high: str
	dflt_network: str
	dflt_tslt_states: str
	dflt_convert_xml: str
	dflt_clear_option: str
	dflt_resume_file: str

class CFGData(BaseModel):
	meta_info: CFGMetaInfo
	node_layout: List[NodeLayout]