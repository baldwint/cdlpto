import datetime as dt
import subprocess
import webbrowser

import click
from dateutil.parser import parse

from .config import date_format
from .email import build_gmail_link
from .pdf import make_pdf


@click.command
@click.option(
    "-c",
    "--comment",
    default="",
    prompt="Enter comment",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="overwrite existing PDF file",
)
@click.argument("date_string")
def main(date_string: str, comment: str, overwrite: bool):
    """Fill out the CDL PTO pdf form"""
    # parse date
    target_day = parse(date_string).date()
    if target_day < dt.date.today():
        print(f"warning: {target_day.strftime(date_format)} is in the past")
    outpath = make_pdf(target_day, comment, overwrite=overwrite)
    print(f"Output written on {str(outpath)}.")
    subprocess.run(["open", outpath])

    webbrowser.open_new(build_gmail_link(target_day))
    print(
        """Now you need to:
    - attach the pdf to the email
    - send the email
    - set an autoresponder in gmail
    - block your google calendar
    - set an autoresponder in the client email
    - block your client calendar
    - set a slack status to away
    """
    )
