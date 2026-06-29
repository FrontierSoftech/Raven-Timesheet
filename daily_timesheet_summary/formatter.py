from .utils import format_hours


def format_summary(summary):
    """Convert aggregated dict into a Raven-friendly markdown summary."""
    employees = summary.get("employees") or {}
    total = summary.get("total") or 0

    if not employees:
        return "📅 Daily Timesheet Summary\n\n_No timesheets submitted today._"

    lines = ["📅 Daily Timesheet Summary"]

    for emp, emp_data in employees.items():
        emp_total = emp_data.get("total", 0)
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"👤 **{emp}** _({format_hours(emp_total)} hrs)_")

        for project, entries in emp_data.get("projects", {}).items():
            lines.append("")
            lines.append(f"{project}")
            for entry in entries:
                task = entry.get("task")
                subject = entry.get("subject")
                hours = entry.get("hours", 0)
                descriptions = entry.get("descriptions", [])

                if task:
                    task_label = subject if subject else task
                    lines.append(f"• Task: {task_label}")
                lines.append(f"  Time: {format_hours(hours)} hrs")
                if descriptions:
                    lines.append(f"  Description: {'; '.join(descriptions)}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"⏱ **Total Hours Today: {format_hours(total)} hrs**")
    return "\n".join(lines)
