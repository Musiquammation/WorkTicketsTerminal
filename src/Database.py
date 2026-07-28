from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dbObjects import *


class Database:
	def __init__(self, database_url: str):
		self.engine = create_engine(database_url, echo=False)

		# Create every table if it does not already exist.
		Base.metadata.create_all(self.engine)

	def session(self) -> Session:
		"""Create a new SQLAlchemy session."""
		return Session(self.engine)

	# ----------------------------------------------------------------------

	def add_status(
		self,
		name: str,
		description: str | None = None,
		color: str = "default",
		bold: bool = False,
		start: bool = False,
		final: bool = False,
	) -> None:
		"""Insert a new status."""

		with self.session() as session:
			session.add(
				Status(
					name=name,
					desc=description,
					color=color,
					bold=bold,
					start=start,
					final=final,
				)
			)
			session.commit()

