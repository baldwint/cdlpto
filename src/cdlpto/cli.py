import datetime as dt
import glob
import os
import subprocess
import webbrowser
from pathlib import Path

import click
from appdirs import user_config_dir
from dateutil.parser import parse

from . import config
from .email import build_gmail_link
from .pdf import make_pdf
from .pto import PTO

CONFIG_DIR = Path(user_config_dir("cdlpto", "baldwint"))
CONFIG_LOC = CONFIG_DIR / "cdlpto.toml"


def onboarding_flow(location: Path) -> config.Config:
    """Set up a config file on first run."""
    print("No config file found.")
    output_dir = Path(os.path.expanduser("~"))
    default_name = subprocess.check_output(["id", "-F"]).decode("utf8").rstrip()
    employee_name = click.prompt("State your name.", default=default_name)
    config.write_default_config(
        location, employee_name=employee_name, output_dir=output_dir
    )
    editor = os.environ.get("EDITOR", "pico")
    print(
        f"I will now drop you into the {editor} editor to edit the file: {location}."
        "\nYou should configure your manager's name and email address there."
        "\nIn addition to editing that file, please place a blank, "
        "signed copy of the PTO form PDF into the same folder as the config."
    )
    click.confirm("Ready?", abort=True, default=True)
    subprocess.check_call([*editor.split(), location])
    return config.load_config(location)


def find_pdf_template(config_dir: Path) -> Path:
    """Find the PDF template and return its path"""
    pdfs = glob.glob(str(config_dir / "*.pdf"))
    if len(pdfs) > 1:
        raise SystemExit(
            f"Sorry, I get confused if there's more than one PDF file in {CONFIG_DIR}."
        )
    elif len(pdfs) != 1:
        raise SystemExit(
            f"I need you to put a blank, signed PTO PDF form into {CONFIG_DIR}."
        )
    (pdf_template,) = pdfs
    return Path(pdf_template)


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
@click.option(
    "-n",
    "--n-days",
    default=1,
    show_default=True,
    type=click.IntRange(min=1),
    help="Number of days to take off",
)
@click.option(
    "-t",
    "--type",
    "leave_type",
    default="pto",
    show_default=True,
    type=click.Choice(["pto", "sick", "holiday", "unpaid"]),
    help="What type of leave: regular PTO, sick leave, floating holiday, or unpaid",
)
@click.option(
    "--draft-email/--no-draft-email",
    "draft_email",
    default=True,
    show_default=True,
    type=bool,
    help="Whether to open a compose window in Gmail",
)
@click.argument("date_string")
def main(
    date_string: str,
    comment: str,
    overwrite: bool,
    n_days: int,
    leave_type: str,
    draft_email: bool,
):
    """Fill out the CDL PTO pdf form"""
    if os.path.exists(CONFIG_LOC):
        cfg = config.load_config(CONFIG_LOC)
    else:
        cfg = onboarding_flow(CONFIG_LOC)
    template_path = find_pdf_template(CONFIG_DIR)
    # parse date
    target_day = parse(date_string).date()
    if target_day < dt.date.today():
        print(f"warning: {target_day.strftime(cfg.date_format)} is in the past")
        click.confirm("Proceed anyway?", abort=True)
    pto = PTO(
        target_day=target_day,
        n_days=n_days,
        leave_type=leave_type,
        comment=comment,
    )
    outpath = make_pdf(
        config=cfg,
        pto=pto,
        template_path=template_path,
        overwrite=overwrite,
    )
    print(f"Output written on {str(outpath)}.")
    subprocess.run(["open", outpath])

    if draft_email:
        webbrowser.open_new(build_gmail_link(config=cfg, pto=pto))
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
