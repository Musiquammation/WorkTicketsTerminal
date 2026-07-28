from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
	Boolean,
	DateTime,
	ForeignKey,
	ForeignKeyConstraint,
	Integer,
	String,
	Text,
)
from sqlalchemy.orm import (
	DeclarativeBase,
	Mapped,
	mapped_column,
)


# ============================================================================
# Base
# ============================================================================

class Base(DeclarativeBase):
	"""Base class for all ORM models."""
	pass


# ============================================================================
# Models
# ============================================================================

class Status(Base):
	"""Represents a ticket status."""

	__tablename__ = "status"

	name: Mapped[str] = mapped_column(String, primary_key=True)
	desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

	color: Mapped[str] = mapped_column(
		String,
		default="default",
	)

	bold: Mapped[bool] = mapped_column(
		Boolean,
		default=False,
	)

	start: Mapped[bool] = mapped_column(Boolean)
	final: Mapped[bool] = mapped_column(Boolean)


class Transition(Base):
	"""Represents a possible transition between two statuses."""

	__tablename__ = "transition"

	origin: Mapped[str] = mapped_column(
		ForeignKey("status.name"),
		primary_key=True,
	)

	target: Mapped[str] = mapped_column(
		ForeignKey("status.name"),
		primary_key=True,
	)

	name: Mapped[Optional[str]] = mapped_column(
		String,
		nullable=True,
	)


class Project(Base):
	"""Represents a project."""

	__tablename__ = "project"

	name: Mapped[str] = mapped_column(String, primary_key=True)

	default_start_status: Mapped[Optional[str]] = mapped_column(
		ForeignKey("status.name"),
		nullable=True,
	)


class Ticket(Base):
	"""Represents a ticket."""

	__tablename__ = "ticket"

	project: Mapped[str] = mapped_column(
		ForeignKey("project.name"),
		primary_key=True,
	)

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
	)

	parent_project: Mapped[Optional[str]] = mapped_column(nullable=True)
	parent_id: Mapped[Optional[int]] = mapped_column(nullable=True)

	title: Mapped[str] = mapped_column(String)
	desc: Mapped[str] = mapped_column(Text)

	status: Mapped[str] = mapped_column(
		ForeignKey("status.name"),
	)

	__table_args__ = (
		ForeignKeyConstraint(
			["parent_project", "parent_id"],
			["ticket.project", "ticket.id"],
		),
	)


class Event(Base):
	"""Represents a ticket history event."""

	__tablename__ = "event"

	project: Mapped[str] = mapped_column(primary_key=True)
	ticket: Mapped[int] = mapped_column(primary_key=True)

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
	)

	date: Mapped[datetime] = mapped_column(
		DateTime,
		default=datetime.utcnow,
	)

	origin: Mapped[str] = mapped_column()
	target: Mapped[str] = mapped_column()

	note: Mapped[str] = mapped_column(Text)

	__table_args__ = (
		ForeignKeyConstraint(
			["project", "ticket"],
			["ticket.project", "ticket.id"],
		),
		ForeignKeyConstraint(
			["origin", "target"],
			["transition.origin", "transition.target"],
		),
	)
