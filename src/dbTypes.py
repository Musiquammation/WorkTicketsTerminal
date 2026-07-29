from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StatusInfo(BaseModel):
	name: str
	desc: Optional[str]
	color: str
	bold: bool
	start: bool
	final: bool

class StatusDetails(StatusInfo):
	targets: List[str]

class TransitionInfo(BaseModel):
	origin: str
	target: str
	name: Optional[str]

class ProjectInfo(BaseModel):
	name: str
	default_start_status: Optional[str]

class TicketInfo(BaseModel):
	project: str
	id: int
	parent_id: Optional[int]
	title: str
	desc: str
	status: str

class EventInfo(BaseModel):
	project: str
	ticket: int
	id: int
	date: datetime
	origin: str
	target: str
	note: Optional[str]
