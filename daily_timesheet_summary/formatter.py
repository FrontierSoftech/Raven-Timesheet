from .utils import format_hours


def format_per_employee_messages(summary):
    """Return one formatted message string per employee."""
    employees = summary.get("employees") or {}
    messages = []

    for emp, emp_data in employees.items():
        emp_total = emp_data.get("total", 0)
        lines = [f"**{emp}** _({format_hours(emp_total)} hrs)_"]

        for project, entries in emp_data.get("projects", {}).items():
            lines.append(project)
            for entry in entries:
                task = entry.get("task")
                subject = entry.get("subject")
                hours = entry.get("hours", 0)
                descriptions = entry.get("descriptions", [])

                if task:
                    task_label = subject if subject else task
                    lines.append(f"Task: {task_label}")
                lines.append(f"Time: {format_hours(hours)} hrs")
                if descriptions:
                    lines.append(f"Description: {'; '.join(descriptions)}")

        messages.append("\n".join(lines))

    return messages
