from __future__ import print_function
from librus import LibrusSession
from configparser import ConfigParser
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json


class Cfg(ConfigParser):
    parser = ConfigParser()

    def __init__(self):
        self.parser.read("config.cfg")
        self.librus = self.parser["librus_credentials"]
        self.librus.login = self.librus["login"]
        self.librus.password = self.librus["password"]


class Librus(LibrusSession):
    exams = []

    def __init__(self, login, password):
        self.login(login, password)
        for exam in self.list_exams():
            self.exams.append(
                self.generate_body(
                    exam.date,
                    exam.category,
                    exam.subject,
                    exam.specification,
                    exam.lesson))

    def convert_to_hour(self, lesson):  # eg. Lesson no. 1 - 7:30 - 8:25
        with open("timetable.json", "r") as f:
            timetable = json.load(f)
            start = [int(timetable["start"][lesson].split()[0]),
                     int(timetable["start"][lesson].split()[1])]
            end = [int(timetable["end"][lesson].split()[0]),
                   int(timetable["end"][lesson].split()[1])]
            return [start, end]

    def generate_body(self, date, category, subject, specification, lesson):
        date = date.replace('-', ' ').split()
        year = int(date[0])
        month = int(date[1])
        day = int(date[2])

        lesson = self.convert_to_hour(lesson)
        start_hour = lesson[0][0]
        start_minute = lesson[0][1]

        end_hour = lesson[1][0]
        end_minute = lesson[1][1]

        start_date = (datetime.datetime(
            year, month, day, start_hour, start_minute).isoformat() + '+01:00')
        end_date = (datetime.datetime(
            year, month, day, end_hour, end_minute).isoformat() + '+01:00')

        return {
            'summary': f"{category} {subject}",
            'description': specification,
            'start': {
                'dateTime': start_date,
                'timeZone': 'Europe/Warsaw',
            },
            'end': {
                'dateTime': end_date,
                'timeZone': 'Europe/Warsaw',
            },
        }


class Calendar():
    def __init__(self):
        self.SCOPE = 'https://www.googleapis.com/auth/calendar'
        self.store = file.Storage('token.json')
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
            self.flow = client.flow_from_clientsecrets(
                'credentials.json', self.SCOPE)
            self.creds = tools.run_flow(self.flow, self.store)
        self.service = build(
            'calendar',
            'v3',
            http=self.creds.authorize(
                Http()))

    def add_exam(self, body):
        self.service.events().insert(calendarId='primary', body=body).execute()


if __name__ == "__main__":
    l = Librus(Cfg().librus.login, Cfg().librus.password)
    cal = Calendar()
    for exam in l.exams:
        if not cal.service.events().list(calendarId='primary',
                                         timeMin=exam['start']['dateTime'], timeMax=exam['end']['dateTime']).execute()['items']:
            cal.add_exam(exam)
