from typing import Optional, List, Dict
from sqlalchemy import create_engine, select, delete, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dbObjects import Base, Status, Transition, Project, Ticket, Event
from dbTypes import StatusInfo, StatusDetails, ProjectInfo, TicketInfo, EventInfo, TransitionInfo

class Database:
	def __init__(self, database_url: str):
		self.engine = create_engine(database_url, echo=False)

		# Create every table if it does not already exist.
		Base.metadata.create_all(self.engine)

	def session(self) -> Session:
		"""Create a new SQLAlchemy session."""
		return Session(self.engine)

	# --- Status & Workflow ---
	def add_status(self, name: str, description: Optional[str] = None, color: str = "default", bold: bool = False, start: bool = False, final: bool = False) -> None:
		with self.session() as session:
			if session.scalar(select(Status).where(Status.name == name)):
				raise ValueError(f"Status '{name}' already exists.")
			
			session.add(Status(name=name, desc=description, color=color, bold=bold, start=start, final=final))
			session.commit()

	def remove_status(self, name: str, force: bool = False) -> None:
		with self.session() as session:
			status = session.get(Status, name)
			if not status:
				raise ValueError("Status not found.")
			
			# Check for events using transitions linked to this status
			transitions = session.scalars(select(Transition).where((Transition.origin == name) | (Transition.target == name))).all()
			for t in transitions:
				events = session.scalars(select(Event).where((Event.origin == t.origin) & (Event.target == t.target))).all()
				if events:
					if not force:
						raise ValueError("Cannot remove status: it is used in events. Use -force to delete them.")
					for e in events:
						session.delete(e)
				session.delete(t)
			
			session.delete(status)
			session.commit()

	def style_status(self, name: str, color: Optional[str], bold: Optional[bool]) -> None:
		with self.session() as session:
			status = session.get(Status, name)
			if not status:
				raise ValueError("Status not found.")
			if color is not None:
				status.color = color
			if bold is not None:
				status.bold = bold
			session.commit()

	def link_statuses(self, origin: str, target: str, transition_name: Optional[str], rename: bool, delete_link: bool, force: bool) -> None:
		with self.session() as session:
			transition = session.scalar(select(Transition).where((Transition.origin == origin) & (Transition.target == target)))
			
			if delete_link:
				if not transition:
					return
				events = session.scalars(select(Event).where((Event.origin == origin) & (Event.target == target))).all()
				if events and not force:
					raise ValueError("Transition used by events. Use -force to delete.")
				if force:
					for e in events:
						session.delete(e)
				session.delete(transition)
			else:
				if transition:
					if not rename:
						raise ValueError("Transition already exists. Use -label to relabel it.")
					transition.name = transition_name
				else:
					session.add(Transition(origin=origin, target=target, name=transition_name))
			session.commit()

	def get_status_details(self, name: Optional[str] = None) -> List[StatusDetails]:
		with self.session() as session:
			query = select(Status)
			if name:
				query = query.where(Status.name == name)
			statuses = session.scalars(query).all()
			
			result = []
			for s in statuses:
				targets = session.scalars(select(Transition.target).where(Transition.origin == s.name)).all()
				result.append(StatusDetails(name=s.name, desc=s.desc, color=s.color, bold=s.bold, start=s.start, final=s.final, targets=list(targets)))
			return result

	# --- Project ---

	def add_project(self, name: str) -> None:
		with self.session() as session:
			session.add(Project(name=name))
			session.commit()

	def remove_project(self, name: str) -> None:
		with self.session() as session:
			project = session.get(Project, name)
			if not project:
				raise ValueError("Project not found.")
			session.delete(project)
			session.commit()

	def list_projects(self) -> List[ProjectInfo]:
		with self.session() as session:
			projects = session.scalars(select(Project)).all()
			return [ProjectInfo(name=p.name, default_start_status=p.default_start_status) for p in projects]

	def update_project(self, name: str, start_status: Optional[str], clean_start: bool) -> ProjectInfo:
		with self.session() as session:
			project = session.get(Project, name)
			if not project:
				raise ValueError("Project not found.")
			
			if clean_start:
				project.default_start_status = None
			elif start_status:
				status = session.get(Status, start_status)
				if not status or not status.start:
					raise ValueError("Status does not exist or is not a start status.")
				project.default_start_status = start_status
			
			session.commit()
			return ProjectInfo(name=project.name, default_start_status=project.default_start_status)

	# --- Ticket ---
	
	def add_ticket(self, project: str, title: str, desc: str, status: Optional[str]) -> TicketInfo:
		with self.session() as session:
			if not status:
				# Find start status
				st = session.scalar(select(Status).where(Status.start == True))
				if not st:
					raise ValueError("No start status found and no status provided.")
				status = st.name
				
			ticket = Ticket(project=project, title=title, desc=desc, status=status)
			session.add(ticket)
			session.commit()
			
			return TicketInfo(project=ticket.project, id=ticket.id, parent_id=ticket.parent_id, title=ticket.title, desc=ticket.desc, status=ticket.status)

	def get_ticket(self, project: str, ticket_id: int) -> Optional[TicketInfo]:
		with self.session() as session:
			t = session.scalar(select(Ticket).where((Ticket.project == project) & (Ticket.id == ticket_id)))
			if t:
				return TicketInfo(project=t.project, id=t.id, parent_id=t.parent_id, title=t.title, desc=t.desc, status=t.status)
			return None

	def delete_ticket(self, project: str, ticket_id: int) -> None:
		with self.session() as session:
			t = session.scalar(select(Ticket).where((Ticket.project == project) & (Ticket.id == ticket_id)))
			if t:
				session.delete(t)
				session.commit()

	def update_ticket(self, project: str, ticket_id: int, title: Optional[str] = None, desc: Optional[str] = None, new_status: Optional[str] = None) -> None:
		with self.session() as session:
			t = session.scalar(select(Ticket).where((Ticket.project == project) & (Ticket.id == ticket_id)))
			if not t:
				raise ValueError("Ticket not found.")
			if title is not None:
				t.title = title
			if desc is not None:
				t.desc = desc
			if new_status is not None:
				t.status = new_status
			session.commit()

	def add_event(self, project: str, ticket_id: int, origin: str, target: str, note: str = "") -> None:
		with self.session() as session:
			session.add(Event(project=project, ticket=ticket_id, origin=origin, target=target, note=note))
			session.commit()

	def get_transitions_from(self, origin: str) -> List[TransitionInfo]:
		with self.session() as session:
			ts = session.scalars(select(Transition).where(Transition.origin == origin)).all()
			return [TransitionInfo(origin=t.origin, target=t.target, name=t.name) for t in ts]

	def get_ticket_history(self, project: str, ticket_id: Optional[int], limit: int = 8) -> List[EventInfo]:
		with self.session() as session:
			query = select(Event).where(Event.project == project).order_by(Event.date.desc())
			if ticket_id is not None:
				query = query.where(Event.ticket == ticket_id)
			if limit:
				query = query.limit(limit)
				
			events = session.scalars(query).all()
			return [EventInfo(project=e.project, ticket=e.ticket, id=e.id, date=e.date, origin=e.origin, target=e.target, note=e.note) for e in events]
			
	def get_all_tickets(self, project: str) -> List[TicketInfo]:
		with self.session() as session:
			tickets = session.scalars(select(Ticket).where(Ticket.project == project)).all()
			return [TicketInfo(project=t.project, id=t.id, parent_id=t.parent_id, title=t.title, desc=t.desc, status=t.status) for t in tickets]

	# --- Choice Helpers ---
	def get_status_names(self) -> List[str]:
		with self.session() as session:
			return list(session.scalars(select(Status.name)).all())
			
	def get_project_names(self) -> List[str]:
		with self.session() as session:
			return list(session.scalars(select(Project.name)).all())
			
	def get_ticket_ids_hex(self, project: str) -> List[str]:
		with self.session() as session:
			ids = session.scalars(select(Ticket.id).where(Ticket.project == project)).all()
			return [hex(i)[2:] for i in ids]


