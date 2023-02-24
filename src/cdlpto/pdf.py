import dataclasses
import datetime as dt
import io
import typing
from pathlib import Path

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .config import Config
from .pto import PTO

XY = typing.Tuple[int, int]


@dataclasses.dataclass
class PDFLayout:
    date: XY
    name: XY
    days: XY
    comment: XY
    checkboxes: typing.Mapping[str, XY]


def write(can, xy, text):
    textobject = can.beginText(*xy)
    textobject.setFont("Helvetica", 12, leading=None)
    textobject.textOut(text)
    can.drawText(textobject)


LAYOUTS = {
    "cdl": PDFLayout(
        date=(120, 598),
        name=(180, 568),
        days=(195, 540),
        comment=(140, 478),
        checkboxes={
            "holiday": (74, 404),
            "pto": (74, 372),
            "sick": (74, 337),
            "unpaid": (74, 304),
        },
    ),
    "kcdl": PDFLayout(
        date=(120, 550),
        name=(180, 520),
        days=(195, 492),
        comment=(140, 433),
        checkboxes={
            "holiday": (74, 359),
            "pto": (74, 329),
            "sick": (74, 296),
            "unpaid": (74, 263),
        },
    ),
}


def write_on_pdf(
    config: Config,
    pto: PTO,
    days: str,
    layout: PDFLayout,
):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    write(can, layout.date, dt.date.today().strftime(config.date_format))
    write(can, layout.name, config.employee_name)
    write(can, layout.days, days)
    write(can, layout.comment, pto.comment)
    write(can, layout.checkboxes[pto.leave_type], "x")

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
    layout = LAYOUTS[config.pdf_layout]
    if pto.n_days == 1:
        days = pto.target_day.strftime(config.date_format)
    else:
        days = (
            f"{pto.n_days} days,"
            f" from {pto.target_day.strftime(config.date_format)}"
            f" through {pto.last_day.strftime(config.date_format)}"
        )

    if pto.leave_type not in layout.checkboxes:
        raise ValueError(
            f"What type of PTO is {pto.leave_type}?"
            f" Expected one of: {layout.checkboxes.keys()}"
        )

    outdir = Path(config.output_dir)
    outpath = outdir / f"{pto.target_day.isoformat()}-Time-Off-Request-Form.pdf"

    new_pdf = write_on_pdf(config, pto, days, layout)

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
