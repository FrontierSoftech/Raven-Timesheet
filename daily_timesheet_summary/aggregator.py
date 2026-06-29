import frappe
from collections import defaultdict
from .utils import get_today, create_logger

logger = create_logger()


def fetch_timesheets(target_date=None):
    """Fetch all submitted Timesheet Detail rows for the given date."""
    target_date = target_date or get_today()

    rows = frappe.db.sql(
        """
        SELECT
            ts.name                                       AS timesheet,
            ts.employee_name                              AS employee,
            tsd.project                                   AS project_id,
            COALESCE(p.project_name, tsd.project)        AS project,
            tsd.task                                      AS task,
            t.subject                                     AS task_subject,
            tsd.hours                                     AS hours,
            tsd.description                               AS description
        FROM `tabTimesheet` ts
        INNER JOIN `tabTimesheet Detail` tsd ON tsd.parent = ts.name
        LEFT JOIN `tabProject` p ON p.name = tsd.project
        LEFT JOIN `tabTask` t ON t.name = tsd.task
        WHERE ts.docstatus = 1
          AND DATE(tsd.from_time) = %(d)s
        """,
        {"d": target_date},
        as_dict=True,
    )

    logger.info(f"Fetched {len(rows)} timesheet rows for {target_date}")
    return rows


def aggregate(rows):
    """
    Group rows as:
        { employee: { total, projects: { project: [ { task, subject, hours, descriptions } ] } } }
    Also returns grand total.
    """
    entry_map = defaultdict(lambda: {"hours": 0.0, "descriptions": [], "subject": None})
    emp_totals = defaultdict(float)
    total = 0.0

    for r in rows:
        employee = r.get("employee") or "(Unknown)"
        project = r.get("project") or "(No Project)"
        task = r.get("task") or None
        subject = r.get("task_subject") or None
        hours = float(r.get("hours") or 0)
        description = (r.get("description") or "").strip()

        key = (employee, project, task)
        entry_map[key]["hours"] += hours
        entry_map[key]["subject"] = subject
        if description:
            entry_map[key]["descriptions"].append(description)
        emp_totals[employee] += hours
        total += hours

    employees = defaultdict(lambda: {"total": 0.0, "projects": defaultdict(list)})
    for (employee, project, task), entry in entry_map.items():
        employees[employee]["total"] = emp_totals[employee]
        employees[employee]["projects"][project].append({
            "task": task,
            "subject": entry["subject"],
            "hours": entry["hours"],
            "descriptions": entry["descriptions"],
        })

    clean = {
        emp: {"total": data["total"], "projects": dict(data["projects"])}
        for emp, data in employees.items()
    }
    return {"employees": clean, "total": total}


