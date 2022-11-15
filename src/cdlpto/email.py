import datetime as dt
import textwrap
from urllib.parse import urlencode

from . import config


def build_gmail_link(target_day: dt.date):
    subject = f"PTO on {target_day.isoformat()}"
    body = textwrap.dedent(
        """\
            {config.manager_name},

            Requesting PTO on {target_day}.

            Thank you!

            {config.signature}"""
    ).format(
        config=config,
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
