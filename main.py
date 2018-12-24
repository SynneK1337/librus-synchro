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
            self.exams.append((exam.category, exam.classroom, exam.date, self.convert_to_hour(exam.lesson), exam.publish_date, exam.specification, exam.subject, exam.teacher))

    def convert_to_hour(self, lesson): # eg. Lesson no. 1 - 7:30 - 8:25
        with open("timetable.json", "r") as f:
            timetable = json.load(f)
            start = [int(timetable["start"][lesson].split()[0]), int(timetable["start"][lesson].split()[1])]
            end = [int(timetable["end"][lesson].split()[0]), int(timetable["end"][lesson].split()[1])]
            return [start, end]

class Calendar():
    def __init__(self):
        self.SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
        self.store = file.Storage('token.json')
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
            self.flow = client.flow_from_clientsecrets('credentials.json', self.SCOPES)
            self.creds = tools.run_flow(self.flow, self.store)
        self.service = build('calendar', 'v3', http=self.creds.authorize(Http()))

    def add_exam(self, date, category, subject, specification, lesson):
        date = date.replace('-', ' ').split()
        year = date[0]
        month = date[1]
        day = date[2]

        start_hour = lesson[0][0]
        start_minute = lesson[0][1]
        
        end_hour = lesson[1][0]
        end_minute = lesson[1][1]

        start_date = datetime.datetime(year, month, day, start_hour, start_minute)
        end_date = datetime.datetime(year, month, day, end_hour, end_minute)

        self.service.events().insert(calendarId="primary", start.TimeZone="Europe/Warsaw", start.dateTime=start_date, end.dateTime=end_date, description=f"{subject} {category} {specification}" )

        '''
        # Call the Calendar API
        self.now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        self.events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        self.events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
'''