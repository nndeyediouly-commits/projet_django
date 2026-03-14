# projects/google_calendar.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_google_flow():
    """Crée le flow OAuth2 pour Google Calendar."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id":     settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
                "token_uri":     "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    return flow


def add_task_to_calendar(credentials_data, task):
    """Ajoute une tâche comme événement dans Google Calendar."""
    credentials = Credentials(**credentials_data)
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': f'📋 {task.title}',
        'description': f'Projet: {task.project.name}\n\n{task.description}',
        'start': {
            'dateTime': task.deadline.isoformat(),
            'timeZone': 'Africa/Dakar',
        },
        'end': {
            'dateTime': task.deadline.isoformat(),
            'timeZone': 'Africa/Dakar',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email',  'minutes': 24 * 60},  # 24h avant
                {'method': 'popup',  'minutes': 60},        # 1h avant
            ],
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()

    return event.get('htmlLink')