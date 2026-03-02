"""Utilitários para geração de PDF com branding NTT Data."""
import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from django.conf import settings
from django.utils import timezone

# Paleta oficial NTT Data
NTT_NAVY  = colors.HexColor("#0A1628")
NTT_BLUE  = colors.HexColor("#0057A8")
NTT_BLUE2 = colors.HexColor("#1A7BC4")
NTT_LIGHT = colors.HexColor("#EBF4FB")
NTT_DARK  = colors.HexColor("#111827")
NTT_GRAY  = colors.HexColor("#6B7280")
NTT_LINE  = colors.HexColor("#E5E7EB")
NTT_WHITE = colors.white
NTT_FOOTER= colors.HexColor("#F3F4F6")
NTT_GREEN = colors.HexColor("#16A34A")

LOGO_PATH = os.path.join(settings.BASE_DIR, "frontend", "static", "img", "ntt_data_logo.png")
PAGE_W, PAGE_H = A4


def _header_footer(canvas_obj, doc, title, subtitle=""):
    canvas_obj.saveState()
    canvas_obj.setFillColor(NTT_NAVY)
    canvas_obj.rect(0, PAGE_H - 2.2*cm, PAGE_W, 2.2*cm, fill=1, stroke=0)
    canvas_obj.setFillColor(NTT_BLUE)
    canvas_obj.rect(0, PAGE_H - 2.35*cm, PAGE_W, 0.18*cm, fill=1, stroke=0)

    if os.path.exists(LOGO_PATH):
        try:
            canvas_obj.drawImage(LOGO_PATH, 1.5*cm, PAGE_H - 1.9*cm,
                width=3.8*cm, height=1.5*cm, preserveAspectRatio=True,
                anchor="sw", mask="auto")
        except Exception:
            pass

    canvas_obj.setFillColor(NTT_WHITE)
    canvas_obj.setFont("Helvetica-Bold", 11)
    canvas_obj.drawRightString(PAGE_W - 1.5*cm, PAGE_H - 1.05*cm, title)
    if subtitle:
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(PAGE_W - 1.5*cm, PAGE_H - 1.6*cm, subtitle)

    canvas_obj.setFillColor(NTT_FOOTER)
    canvas_obj.rect(0, 0, PAGE_W, 1.1*cm, fill=1, stroke=0)
    canvas_obj.setStrokeColor(NTT_LINE)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(0, 1.1*cm, PAGE_W, 1.1*cm)
    canvas_obj.setFillColor(NTT_GRAY)
    canvas_obj.setFont("Helvetica", 7.5)
    now = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")
    canvas_obj.drawString(1.5*cm, 0.4*cm, f"Gerado em {now}  —  NTT Data © {timezone.now().year}")
    canvas_obj.drawRightString(PAGE_W - 1.5*cm, 0.4*cm, f"Página {doc.page}")
    canvas_obj.restoreState()


def build_pdf(title, subtitle, columns, rows, filename):
    """PDF simples com tabela única."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=3*cm, bottomMargin=1.8*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("NTTTitle", parent=styles["Heading1"],
        fontSize=14, textColor=NTT_NAVY, spaceAfter=4, fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("NTTSub", parent=styles["Normal"],
        fontSize=9, textColor=NTT_GRAY, spaceAfter=12)
    cell_style = ParagraphStyle("NTTCell", parent=styles["Normal"],
        fontSize=8, textColor=NTT_DARK, leading=11)

    story = [Paragraph(title, title_style)]
    if subtitle:
        story.append(Paragraph(subtitle, sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=NTT_BLUE, spaceAfter=10))

    avail_w = PAGE_W - 3*cm
    col_w = avail_w / len(columns)
    table_data = [columns] + [
        [Paragraph(str(c), cell_style) for c in row] for row in rows
    ]
    table = Table(table_data, colWidths=[col_w]*len(columns), repeatRows=1)
    table.setStyle(_base_table_style())
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Total de registros: <b>{len(rows)}</b>",
        ParagraphStyle("t", parent=styles["Normal"], fontSize=8,
                       textColor=NTT_GRAY, alignment=TA_RIGHT)))

    doc.build(story,
        onFirstPage=lambda c, d: _header_footer(c, d, title, subtitle),
        onLaterPages=lambda c, d: _header_footer(c, d, title, subtitle))
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf_agrupado(title, subtitle, grupos, filename):
    """
    PDF com dados agrupados.

    grupos: lista de dicts com:
      {
        'titulo':    str,              # ex: nome do colaborador
        'subtitulo': str,              # ex: cargo / matrícula
        'colunas':   [str, ...],       # cabeçalhos das colunas
        'linhas':    [[val, ...], ...] # dados
      }
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=3*cm, bottomMargin=1.8*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("NTTTitle", parent=styles["Heading1"],
        fontSize=14, textColor=NTT_NAVY, spaceAfter=4, fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("NTTSub", parent=styles["Normal"],
        fontSize=9, textColor=NTT_GRAY, spaceAfter=14)
    grupo_title_style = ParagraphStyle("GTitle", parent=styles["Normal"],
        fontSize=10, textColor=NTT_WHITE, fontName="Helvetica-Bold",
        leftIndent=6, leading=14)
    grupo_sub_style = ParagraphStyle("GSub", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#93C5FD"),
        leftIndent=6, leading=11, spaceAfter=4)
    cell_style = ParagraphStyle("NTTCell", parent=styles["Normal"],
        fontSize=8, textColor=NTT_DARK, leading=11)
    total_style = ParagraphStyle("NTTTotal", parent=styles["Normal"],
        fontSize=8, textColor=NTT_GRAY, alignment=TA_RIGHT)

    story = [Paragraph(title, title_style)]
    if subtitle:
        story.append(Paragraph(subtitle, sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=NTT_BLUE, spaceAfter=14))

    avail_w = PAGE_W - 3*cm
    total_linhas = 0

    for grupo in grupos:
        colunas = grupo["colunas"]
        linhas  = grupo["linhas"]
        total_linhas += len(linhas)
        col_w = avail_w / len(colunas)

        # Cabeçalho do grupo — fundo azul marinho
        header_table = Table(
            [[Paragraph(grupo["titulo"], grupo_title_style)]],
            colWidths=[avail_w]
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NTT_NAVY),
            ("TOPPADDING",    (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))

        # Subtítulo do grupo (cargo / matrícula)
        sub_table = Table(
            [[Paragraph(grupo.get("subtitulo", ""), grupo_sub_style)]],
            colWidths=[avail_w]
        )
        sub_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), NTT_BLUE),
            ("TOPPADDING",    (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))

        # Tabela de linhas do grupo
        table_data = [colunas] + [
            [Paragraph(str(c), cell_style) for c in row] for row in linhas
        ]
        data_table = Table(table_data, colWidths=[col_w]*len(colunas), repeatRows=1)
        data_table.setStyle(_base_table_style(header_bg=NTT_BLUE2))

        # Agrupa tudo para não quebrar no meio
        story.append(KeepTogether([
            header_table,
            sub_table,
            data_table,
            Spacer(1, 12),
        ]))

    story.append(Paragraph(
        f"Total de registros: <b>{total_linhas}</b>  |  Grupos: <b>{len(grupos)}</b>",
        total_style
    ))

    doc.build(story,
        onFirstPage=lambda c, d: _header_footer(c, d, title, subtitle),
        onLaterPages=lambda c, d: _header_footer(c, d, title, subtitle))
    buffer.seek(0)
    return buffer.getvalue()


def _base_table_style(header_bg=None):
    if header_bg is None:
        header_bg = NTT_NAVY
    return TableStyle([
        ("BACKGROUND",    (0,0), (-1, 0), header_bg),
        ("TEXTCOLOR",     (0,0), (-1, 0), NTT_WHITE),
        ("FONTNAME",      (0,0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1, 0), 8),
        ("TOPPADDING",    (0,0), (-1, 0), 6),
        ("BOTTOMPADDING", (0,0), (-1, 0), 6),
        ("LEFTPADDING",   (0,0), (-1, 0), 8),
        ("LINEBELOW",     (0,0), (-1, 0), 2, NTT_BLUE),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 8),
        ("TOPPADDING",    (0,1), (-1,-1), 5),
        ("BOTTOMPADDING", (0,1), (-1,-1), 5),
        ("LEFTPADDING",   (0,1), (-1,-1), 8),
        ("RIGHTPADDING",  (0,1), (-1,-1), 6),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [NTT_WHITE, NTT_LIGHT]),
        ("LINEBELOW",     (0,1), (-1,-1), 0.4, NTT_LINE),
        ("BOX",           (0,0), (-1,-1), 0.8, NTT_BLUE),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ])
