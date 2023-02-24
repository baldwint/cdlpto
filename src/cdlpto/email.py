import textwrap
from urllib.parse import urlencode

from .config import Config
from .pto import PTO

leave_types = {
    "pto": "PTO",
    "holiday": "floating holiday",
    "sick": "sick leave",
    "unpaid": "unpaid time off",
}


def build_gmail_link(config: Config, pto: PTO):
    pto_type = leave_types[pto.leave_type]
    pto_type_cap = pto_type if pto_type.isupper() else pto_type.capitalize()
    if pto.n_days == 1:
        subject = f"{pto_type_cap} on {pto.target_day.isoformat()}"
        message = (
            f"Requesting {pto_type}"
            f" on {pto.target_day.strftime(config.date_format)}."
        )
    else:
        subject = (
            f"{pto_type_cap}"
            f" from {pto.target_day.isoformat()} to {pto.last_day.isoformat()}"
        )
        message = (
            f"Requesting {pto.n_days} days of {pto_type}"
            f" from {pto.target_day.strftime(config.date_format)}"
            f" to {pto.last_day.strftime(config.date_format)}."
        )
    body = textwrap.dedent(
        """\
            {config.manager_name},

            {message}

            Thank you!

            {config.signature}"""
    ).format(config=config, message=message)
    qs = urlencode(
        dict(
            view="cm",
            fs=1,
            to=config.manager_email,
            su=subject,
            body=body,
        )
    )
    return f"https://mail.google.com/mail/u/{config.gmail_account_index}/?" + qs
