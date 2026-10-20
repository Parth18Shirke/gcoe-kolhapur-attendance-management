import io
import csv

def generate_attendance_csv(headers: list, rows: list) -> io.StringIO:
    """
    Generates a CSV string buffer for spreadsheet export.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    output.seek(0)
    return output
