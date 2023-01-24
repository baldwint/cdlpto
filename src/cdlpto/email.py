import datetime as dt
import textwrap
from urllib.parse import urlencode

from . import config

leave_types = {
    "pto": "PTO",
    "holiday": "floating holiday",
    "sick": "sick leave",
    "unpaid": "unpaid time off",
}


def build_gmail_link(target_day: dt.date, leave_type: str):
    pto_type = leave_types[leave_type]
    subject = f"{pto_type.capitalize()} on {target_day.isoformat()}"
    body = textwrap.dedent(
        """\
            {config.manager_name},

            Requesting {pto_type} on {target_day}.

            Thank you!

            {config.signature}"""
    ).format(
        config=config,
        pto_type=pto_type,
        target_day=target_day.strftime(config.date_format),
    )
    qs = urlencode(
        dict(
            view="cm",
            fs=1,
            to=config.manager_email,
            su=subject,
            body=body,
        )
    )
    return "https://mail.google.com/mail/u/1/?" + qs
