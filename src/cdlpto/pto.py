import dataclasses
import datetime as dt
import typing


@dataclasses.dataclass
class PTO:
    target_day: dt.date
    n_days: int = 1
    leave_type: str = "pto"
    comment: typing.Optional[str] = None

    @property
    def last_day(self):
        if self.n_days > 1:
            return self.target_day + dt.timedelta(days=self.n_days - 1)
        else:
            return self.target_day
