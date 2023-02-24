import datetime as dt
import io
from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .config import Config
from .pto import PTO


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
    pto: PTO,
    days: str,
):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    write(can, (120, 598), dt.date.today().strftime(config.date_format))
    write(can, (180, 568), config.employee_name)
    write(can, (195, 540), days)
    write(can, (140, 478), pto.comment)
    write(can, checkboxes[pto.leave_type], "x")

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    return new_pdf


def make_pdf(
    config: Config,
    pto: PTO,
    template_path: Path,
    overwrite: bool = False,
) -> str:
    if pto.n_days == 1:
        days = pto.target_day.strftime(config.date_format)
    else:
        days = (
            f"{pto.n_days} days,"
            f" from {pto.target_day.strftime(config.date_format)}"
            f" through {pto.last_day.strftime(config.date_format)}"
        )

    if pto.leave_type not in checkboxes:
        raise ValueError(
            f"What type of PTO is {pto.leave_type}? Expected one of: {checkboxes.keys()}"
        )

    outdir = Path(config.output_dir)
    outpath = outdir / f"{pto.target_day.isoformat()}-Time-Off-Request-Form.pdf"

    new_pdf = write_on_pdf(config, pto, days)

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
