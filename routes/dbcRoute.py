from controller.dbcController import DBCController, DBCDecoder
from fastapi import APIRouter, File, UploadFile, HTTPException
from io import StringIO
from schemas import CANFrame, FrameSignal
from typing import List, Optional, Union

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
