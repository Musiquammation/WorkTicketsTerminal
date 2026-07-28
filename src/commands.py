def cb_workflow_add(kwargs: dict): pass
def cb_workflow_remove(kwargs: dict): pass
def cb_workflow_style(kwargs: dict): pass
def cb_workflow_link(kwargs: dict): pass
def cb_workflow_show(kwargs: dict): pass

def cb_project_add(kwargs: dict): pass
def cb_project_remove(kwargs: dict): pass
def cb_project_list(kwargs: dict): pass
def cb_project_update(kwargs: dict): pass
def cb_project_login(kwargs: dict): pass

def cb_ticket_list(kwargs: dict): pass
def cb_ticket_add(kwargs: dict): pass
def cb_ticket_delete(kwargs: dict): pass
def cb_ticket_rename(kwargs: dict): pass
def cb_ticket_redesc(kwargs: dict): pass
def cb_ticket_move(kwargs: dict): pass
def cb_ticket_history(kwargs: dict): pass


# --- Placeholder choices functions ---
def get_status_choices() -> list[str]: return []
def get_color_choices() -> list[str]: return ["default", "red", "green", "blue", "yellow"]
def get_project_choices() -> list[str]: return []
def get_ticket_choices() -> list[str]: return []
