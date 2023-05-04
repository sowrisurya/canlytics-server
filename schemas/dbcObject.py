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