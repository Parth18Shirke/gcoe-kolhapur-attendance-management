import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_attendance_pdf(report_title: str, subtitle: str, headers: list, rows: list, is_landscape: bool = False) -> io.BytesIO:
    """
    Generates a standardized A4 PDF document using ReportLab with exact page geometry.
    """
    buffer = io.BytesIO()
    pagesize = landscape(A4) if is_landscape else A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a')
    )
    sub_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1, # Center
        textColor=colors.HexColor('#475569')
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )
    header_cell_style = ParagraphStyle(
        'HeaderCellText',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("COLLEGE ATTENDANCE MANAGEMENT SYSTEM", sub_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(subtitle, sub_style))
    elements.append(Spacer(1, 15))

    # Table Construction
    table_data = []
    # Header row
    table_data.append([Paragraph(h, header_cell_style) for h in headers])

    for row in rows:
        table_data.append([Paragraph(str(val), cell_style) for val in row])

    col_count = len(headers)
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # Signatures
    sig_data = [
        ["Prepared By: __________________", "Class Coordinator: __________________", "H.O.D.: __________________"]
    ]
    sig_table = Table(sig_data)
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
