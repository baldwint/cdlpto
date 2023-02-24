import dataclasses
from pathlib import Path

import tomli


@dataclasses.dataclass
class Config:
    date_format: str
    employee_name: str
    output_dir: Path
    manager_email: str
    manager_name: str
    signature: str
    gmail_account_index: int = 0
    pdf_layout: str = "kcdl"


def load_config(location: Path) -> Config:
    try:
        with open(location, "rb") as fl:
            conf = tomli.load(fl)
        config = Config(**conf)
    except (TypeError, tomli.TOMLDecodeError):
        print(f"Corrupted config at {location}.")
        raise
    return config


def write_default_config(location: Path, employee_name: str, output_dir: Path):
    contents = (
        r"""date_format = "%A, %-d %B %Y"
employee_name = "{employee_name}"
output_dir = "{output_dir}"
manager_email = "manager.name@kinandcarta.com"
manager_name = "Stef"
signature = "{employee_name}\nJob Title\nKin + Carta Data Labs"
gmail_account_index = 0
pdf_layout = "kcdl"
"""
    ).format(employee_name=employee_name, output_dir=output_dir)
    location.parent.mkdir(exist_ok=True, parents=True)
    with open(location, "x") as fl:
        fl.write(contents)
