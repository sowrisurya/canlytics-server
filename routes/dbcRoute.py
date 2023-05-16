from controller.dbcController import DBCController, DBCDecoder
from fastapi import APIRouter, File, UploadFile, HTTPException
from io import StringIO
from schemas import (
	CANFrame, 
	FrameSignal, 
	CFGData,
	ECUNetworkInfo,
	NetworkNode,
	NodeLayout,
	CFGMetaInfo,
)
from typing import List, Optional, Union
from utils import readParseConfigFile

dbcRouter = APIRouter(
    prefix="/dbc",
    tags=["DBC CAN Message"],
    responses={404: {"description": "Not found"}},
)

@dbcRouter.post("/upload-dbc", response_model=Union[List[CANFrame], List[FrameSignal]])
async def upload_dbc(dbc_file: UploadFile = File(...), frame_id: Optional[int] = None):
	data = await dbc_file.read()
	file_data = StringIO(data.decode("utf-8"))
	dbc_decoder = DBCDecoder(file = file_data)
	if frame_id:
		return dbc_decoder.get_frame_signals(frame_id)
	elif frame_id == 0:
		return dbc_decoder.get_all_frame_ids(include_signals=False)
	else:
		return dbc_decoder.get_all_frame_ids(include_signals=True)

@dbcRouter.post("/upload-cfg", response_model=CFGData)
async def upload_dbc(cfg_file: UploadFile = File(...)):
	data = await cfg_file.read()
	file_data = StringIO(data.decode("utf-8"))
	meta_info, ecu_nodes = readParseConfigFile(configFile=file_data)
	return CFGData(
		meta_info = CFGMetaInfo(
			config_name = meta_info.get("ConfigName", ""), 
			config_version = meta_info.get("ConfigVersion", ""), 
			config_vehicle = meta_info.get("ConfigVehicle", ""), 
			config_veh_init = meta_info.get("ConfigVehInit", ""), 
			protocol_hsc = meta_info.get("ProtocolHSC", ""), 
			dflt_port_num = meta_info.get("DfltPortNum", ""), 
			dflt_port_high = meta_info.get("DfltPortHigh", ""), 
			dflt_network = meta_info.get("DfltNetwork", ""), 
			dflt_tslt_states = meta_info.get("DfltTstStates", ""), 
			dflt_convert_xml = meta_info.get("DfltConvertXML", ""), 
			dflt_clear_option = meta_info.get("DfltClearOption", ""), 
			dflt_resume_file = meta_info.get("DfltResumeFile", ""), 
		), 
		node_layout = ecu_nodes
	)
