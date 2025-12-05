import pandas as pd
from io import BytesIO
from openpyxl.styles import PatternFill, Font
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.table import WD_TABLE_ALIGNMENT

def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Upah")
        sheet = writer.sheets["Upah"]

        for i, col in enumerate(df.columns):
            sheet.column_dimensions[chr(65 + i)].width = max(df[col].astype(str).map(len).max(), len(col)) + 2

        for cell in sheet[1]:
            cell.font = Font(bold=True)

        for idx, row in df.iterrows():
            if row["Bulan"] == "Total":
                for col_idx in range(len(df.columns)):
                    cell = sheet.cell(idx + 2, col_idx + 1)
                    cell.fill = PatternFill(start_color="FFF3B0", fill_type="solid")
                    cell.font = Font(bold=True)

    return output.getvalue()


def export_word(df):
    doc = Document()
    doc.add_heading("Lampiran Kekurangan Upah", level=1)

    table = doc.add_table(rows=1, cols=len(df.columns), style="Table Grid")
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr[i].text = col
        hdr[i].paragraphs[0].runs[0].font.bold = True

    for idx, row in df.iterrows():
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            if row["Bulan"] == "Total":
                r = cells[i].paragraphs[0].runs[0]
                r.font.bold = True
                shd = OxmlElement("w:shd")
                shd.set(qn("w:fill"), "FFF176")
                cells[i]._tc.get_or_add_tcPr().append(shd)

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
