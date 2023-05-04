from pydantic import BaseModel

class ResponseSchema(BaseModel):
	message: str
	status: int
	error: str = None
	data: dict = None