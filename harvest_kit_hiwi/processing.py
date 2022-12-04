import datetime
from typing import List

from dateutil import parser


class TimeSpan:

    def __init__(self,
                 start: datetime.datetime,
                 end: datetime.datetime,
                 description_set: set = set()):
        self.start_datetime = start
        self.end_datetime = end
        self.description_set = description_set

        self.time_delta = self.end_datetime - self.start_datetime
        self.duration = self.time_delta.seconds / 3600

    @property
    def description(self):
        return ', '.join(self.description_set)

    def collides_with(self, other: 'TimeSpan'):
        if self.start_datetime < other.start_datetime:
            return self.end_datetime > other.start_datetime
        else:
            return other.end_datetime > self.start_datetime

    def modify_end(self, seconds: float):
        time_delta = datetime.timedelta(seconds=abs(seconds))
        if seconds > 0:
            self.end_datetime += time_delta
        else:
            self.end_datetime -= time_delta

        self.time_delta = self.end_datetime - self.start_datetime
        self.duration = self.time_delta.seconds / 3600

    def merge(self, other: 'TimeSpan'):
        start_datetime = self.start_datetime
        end_datetime = start_datetime + datetime.timedelta(hours=self.duration + other.duration)
        description_set = set([*self.description_set, *other.description_set])

        return self.__class__(
            start_datetime,
            end_datetime,
            description_set
        )

    def to_dict(self) -> dict:
        return {
            'start': self.start_datetime.isoformat(),
            'end': self.end_datetime.isoformat(),
            'description_set': list(self.description_set)
        }

    # -- MAGIC METHODS --

    def __str__(self):
        return (f'TimeSpan(start={self.start_datetime}, '
                f'end={self.end_datetime}, '
                f'duration={self.duration}, '
                f'descriptions="{self.description}")')

    def __add__(self, other):
        if isinstance(other, int):
            return self
        elif isinstance(other, TimeSpan):
            return self.merge(other)

    def __and__(self, other):
        return self.collides_with(other)

    def __gt__(self, other):
        return self.start_datetime > other.start_datetime

    def __lt__(self, other):
        return self.start_datetime > other.start_datetime

    # -- CLASS METHODS --

    @classmethod
    def from_time_entry(cls, time_entry: dict):
        start = parser.parse(time_entry['created_at'])
        hours = time_entry['hours']

        time_delta = datetime.timedelta(hours=hours)
        end = start + time_delta

        description = time_entry['task']['name']
        descriptions = {description}

        return cls(start, end, descriptions)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            datetime.datetime.fromisoformat(data['start']),
            datetime.datetime.fromisoformat(data['end']),
            set(data['description_set'])
        )


class ArbeitszeitData:

    def __init__(self,
                 time_spans: List[TimeSpan],
                 name: str,
                 personnel_number: str,
                 institute: str,
                 working_hours: float,
                 hourly_rate: float,
                 carry_over: float,
                 leave: float,
                 month: int,
                 year: int):
        self.time_spans = time_spans
        self.name = name
        self.personnel_number = personnel_number
        self.institute = institute
        self.working_hours = working_hours
        self.hourly_rate = hourly_rate
        self.leave = leave
        self.carry_over_before = carry_over
        self.month = month
        self.year = year

        # ~ computed properties
        self.total_time_delta = datetime.timedelta(hours=0)
        for ts in self.time_spans:
            self.total_time_delta += ts.time_delta

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'personnel_number': self.personnel_number,
            'institute': self.institute,
            'working_hours': self.working_hours,
            'hourly_rate': self.hourly_rate,
            'leave': self.leave,
            'carry_over': self.carry_over_before,
            'month': self.month,
            'year': self.year,
            'time_spans': [ts.to_dict() for ts in self.time_spans]
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            personnel_number=data['personnel_number'],
            institute=data['institute'],
            working_hours=data['working_hours'],
            hourly_rate=data['hourly_rate'],
            carry_over=data['carry_over'],
            leave=data['leave'],
            month=data['month'],
            year=data['year'],
            time_spans=[TimeSpan.from_dict(d) for d in data['time_spans']],
        )
