from Database import Database

def cb_workflow_add(db: Database, kwargs: dict[str,str]): pass
def cb_workflow_remove(db: Database, kwargs: dict): pass
def cb_workflow_style(db: Database, kwargs: dict): pass
def cb_workflow_link(db: Database, kwargs: dict): pass
def cb_workflow_show(db: Database, kwargs: dict): pass

def cb_project_add(db: Database, kwargs: dict): pass
def cb_project_remove(db: Database, kwargs: dict): pass
def cb_project_list(db: Database, kwargs: dict): pass
def cb_project_update(db: Database, kwargs: dict): pass
def cb_project_login(db: Database, kwargs: dict): pass

def cb_ticket_list(db: Database, kwargs: dict): pass
def cb_ticket_add(db: Database, kwargs: dict): pass
def cb_ticket_delete(db: Database, kwargs: dict): pass
def cb_ticket_rename(db: Database, kwargs: dict): pass
def cb_ticket_redesc(db: Database, kwargs: dict): pass
def cb_ticket_move(db: Database, kwargs: dict): pass
def cb_ticket_history(db: Database, kwargs: dict): pass


# --- Placeholder choices functions ---
def get_status_choices(db: Database) -> list[str]: return []
def get_color_choices(db: Database) -> list[str]: return ["default", "red", "green", "blue", "yellow"]
def get_project_choices(db: Database) -> list[str]: return []
def get_ticket_choices(db: Database) -> list[str]: return []
