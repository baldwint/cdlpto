#!/usr/bin/env python
# coding: utf-8

import datetime as dt
import io
from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .config import Config


def write(can, xy, text):
    textobject = can.beginText(*xy)
    textobject.setFont("Helvetica", 12, leading=None)
    textobject.textOut(text)
    can.drawText(textobject)


checkboxes = {
    "holiday": (74, 404),
    "pto": (74, 372),
    "sick": (74, 337),
    "unpaid": (74, 304),
}


def write_on_pdf(
    config: Config,
    days: str,
    comment: str = "",
    leave_type: str = "pto",
):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    write(can, (120, 598), dt.date.today().strftime(config.date_format))
    write(can, (180, 568), config.employee_name)
    write(can, (195, 540), days)
    write(can, (140, 478), comment)
    write(can, checkboxes[leave_type], "x")

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    return new_pdf


def make_pdf(
    config: Config,
    template_path: Path,
    target_day: dt.date,
    comment: str = "",
    overwrite: bool = False,
    n_days: int = 1,
    leave_type: str = "pto",
) -> str:
    if n_days < 1:
        raise ValueError("take at least one whole day off!")
    elif n_days == 1:
        days = target_day.strftime(config.date_format)
    else:
        last_day = target_day + dt.timedelta(days=n_days - 1)
        days = (
            f"{n_days} days,"
            f" from {target_day.strftime(config.date_format)}"
            f" through {last_day.strftime(config.date_format)}"
        )

    if leave_type not in checkboxes:
        raise ValueError(
            f"What type of PTO is {leave_type}? Expected one of: {checkboxes.keys()}"
        )

    outdir = Path(config.output_dir)
    outpath = outdir / f"{target_day.isoformat()}-Time-Off-Request-Form.pdf"

    new_pdf = write_on_pdf(config, days, comment, leave_type)

    # read your existing PDF
    with open(template_path, "rb") as fl:
        existing_pdf = PdfFileReader(fl)
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))

        # add the "watermark" (which is the new pdf) on the existing page
        output = PdfFileWriter()
        output.addPage(page)

        # finally, write "output" to a real file
        with open(outpath, "wb" if overwrite else "xb") as outputStream:
            output.write(outputStream)
    return str(outpath)
