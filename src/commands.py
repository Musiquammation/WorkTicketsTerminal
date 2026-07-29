import os
import json
import tempfile
import subprocess
from typing import Any, List, Optional
from Database import Database

# --- CLI Context Helpers ---

current_project = None

def require_project(kwargs: dict[str, Any]) -> str:
    """Gets project from args, falls back to config, or raises Error."""
    proj = kwargs.get("-project")
    if not proj:
        proj = current_project
        
    if not proj:
        raise ValueError("No project specified. Use 'project login <name>' or add -project <name>.")
    
    return proj

def hex_to_int(hex_str: str) -> int:
    return int(hex_str, 16)

def int_to_hex(id_int: int, padding: int = 1) -> str:
    return hex(id_int)[2:].zfill(padding)

def open_vim(initial_content: str = "") -> str:
    """Opens vim to edit a text string."""
    with tempfile.NamedTemporaryFile(suffix=".tmp", mode='w+', delete=False) as tf:
        tf.write(initial_content)
        tf.flush()
        fname = tf.name
    subprocess.call(['vim', fname])
    with open(fname, 'r') as f:
        content = f.read().strip()
    os.remove(fname)
    return content

# --- Choice Functions ---

def get_status_choices(db: Database) -> List[str]:
    return db.get_status_names()

def get_color_choices(db: Database) -> List[str]:
    return ["default", "red", "green", "blue", "yellow"]

def get_project_choices(db: Database) -> List[str]:
    return db.get_project_names()

def get_ticket_choices(db: Database) -> List[str]:
    global current_project
    if not current_project:
        return []
    return db.get_ticket_ids_hex(current_project)

# --- Callbacks ---

def cb_workflow_add(db: Database, kwargs: dict[str, Any]):
    db.add_status(
        name=kwargs["name"],
        description=kwargs.get("-desc"),
        color=kwargs.get("-color", "default"),
        bold=kwargs.get("-bold", False),
        start=kwargs.get("-start", False),
        final=kwargs.get("-final", False),
    )
    print(f"Status '{kwargs['name']}' added.")

def cb_workflow_remove(db: Database, kwargs: dict[str, Any]):
    db.remove_status(kwargs["name"], force=kwargs.get("-force", False))
    print(f"Status '{kwargs['name']}' removed.")

def cb_workflow_style(db: Database, kwargs: dict[str, Any]):
    db.style_status(
        name=kwargs["name"],
        color=kwargs.get("-color"),
        bold=kwargs.get("-bold")
    )
    print(f"Status '{kwargs['name']}' style updated.")

def cb_workflow_link(db: Database, kwargs: dict[str, Any]):
    db.link_statuses(
        origin=kwargs["origin"],
        target=kwargs["target"],
        transition_name=kwargs.get("-label"),
        rename="-label" in kwargs,
        delete_link=kwargs.get("-delete", False),
        force=kwargs.get("-force", False)
    )
    print("Transition processed.")

def cb_workflow_show(db: Database, kwargs: dict[str, Any]):
    status_name = kwargs.get("status")
    details = db.get_status_details(status_name)
    for s in details:
        print(f"Status: {s.name}")
        if s.desc:
            print(f"Desc: {s.desc}")
        print(f"Targets: [{', '.join(s.targets)}]")
        print("-" * 20)

def cb_project_add(db: Database, kwargs: dict[str, Any]):
    db.add_project(kwargs["name"])
    print(f"Project '{kwargs['name']}' added.")

def cb_project_remove(db: Database, kwargs: dict[str, Any]):
    if not kwargs.get("-confirm"):
        raise ValueError("Missing -confirm flag to delete project.")
    db.remove_project(kwargs["name"])
    print(f"Project '{kwargs['name']}' removed.")

def cb_project_list(db: Database, kwargs: dict[str, Any]):
    projects = db.list_projects()
    for p in projects:
        print(f"- {p.name} (Start: {p.default_start_status or 'None'})")

def cb_project_update(db: Database, kwargs: dict[str, Any]):
    p = db.update_project(
        name=require_project(kwargs), # assuming we update current project if not explicitly designed otherwise
        start_status=kwargs.get("-start"),
        clean_start=kwargs.get("-cleanStart", False)
    )
    print(f"Updated Project {p.name}: Start Status is now {p.default_start_status}")

def cb_project_login(db: Database, kwargs: dict[str, Any]):
    global current_project
    name = kwargs.get("projectName")
    if name:
        current_project = name
        print(f"Logged into project '{name}'.")
    else:
        if current_project:
            print(f"Current project: {current_project}")
        else:
            print("No project currently active.")

def cb_ticket_list(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    tickets = db.get_all_tickets(proj)
    
    # Calculate padding for hex IDs dynamically
    max_hex_len = max([len(hex(t.id)[2:]) for t in tickets], default=1)
    
    # Very basic flat listing, to be expanded into proper tree logic later
    for t in tickets:
        hex_id = int_to_hex(t.id, max_hex_len)
        print(f"{hex_id} [{t.status}] {t.title}")

def cb_ticket_add(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    title = kwargs.get("-title")
    desc = kwargs.get("-desc")
    
    if not title or not desc:
        content = open_vim(f"{title or ''}\n\n{desc or ''}")
        parts = content.split('\n\n', 1)
        title = parts[0] if len(parts) > 0 else ""
        desc = parts[1] if len(parts) > 1 else ""

    ticket = db.add_ticket(project=proj, title=title, desc=desc, status=kwargs.get("-status"))
    print(f"Ticket {int_to_hex(ticket.id)} created with status [{ticket.status}].")

def cb_ticket_delete(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    ticket_id = hex_to_int(kwargs["id"])
    db.delete_ticket(proj, ticket_id)
    print(f"Ticket {kwargs['id']} deleted.")

def cb_ticket_rename(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    ticket_id = hex_to_int(kwargs["id"])
    ticket = db.get_ticket(proj, ticket_id)
    if not ticket:
        raise ValueError("Ticket not found")

    title = kwargs.get("-title")
    if not title:
        init_content = "" if kwargs.get("-emptyVim") else ticket.title
        title = open_vim(init_content)

    db.update_ticket(proj, ticket_id, title=title)
    print(f"Ticket {kwargs['id']} renamed.")

def cb_ticket_redesc(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    ticket_id = hex_to_int(kwargs["id"])
    ticket = db.get_ticket(proj, ticket_id)
    if not ticket:
        raise ValueError("Ticket not found")

    desc = kwargs.get("-desc")
    if not desc:
        init_content = "" if kwargs.get("-emptyVim") else ticket.desc
        desc = open_vim(init_content)

    db.update_ticket(proj, ticket_id, desc=desc)
    print(f"Ticket {kwargs['id']} description updated.")

def cb_ticket_move(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    ticket_id = hex_to_int(kwargs["id"])
    ticket = db.get_ticket(proj, ticket_id)
    if not ticket:
        raise ValueError("Ticket not found.")
        
    target_status = kwargs.get("status")
    
    if not target_status:
        transitions = db.get_transitions_from(ticket.status)
        print(f"Accessible statuses from '{ticket.status}':")
        for t in transitions:
            print(f"- {t.target} (Transition: {t.name or 'Unnamed'})")
        return

    # Assuming transition exists logic check happens here or in DB
    db.update_ticket(proj, ticket_id, new_status=target_status)
    db.add_event(proj, ticket_id, origin=ticket.status, target=target_status)
    print(f"Ticket {kwargs['id']} moved to [{target_status}].")

def cb_ticket_history(db: Database, kwargs: dict[str, Any]):
    proj = require_project(kwargs)
    ticket_id = hex_to_int(kwargs["id"]) if kwargs.get("id") else None
    limit = kwargs.get("-limit", 8)
    
    events = db.get_ticket_history(proj, ticket_id, limit)
    for e in events:
        t_id_str = int_to_hex(e.ticket)
        print(f"[{e.date}] Ticket {t_id_str} | {e.origin} -> {e.target} | {e.note or ''}")