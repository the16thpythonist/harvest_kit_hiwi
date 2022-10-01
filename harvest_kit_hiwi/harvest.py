import requests
from typing import List


class HarvestApi:

    def __init__(self,
                 url: str,
                 account_id: str,
                 account_token: str):
        self.url = url
        self.account_id = account_id
        self.account_token = account_token

        # ~ computed properties
        self.time_entries_url = self.url + 'time_entries'
        self.projects_url = self.url + 'projects'

        # ~ setting up the remote session
        self.session = requests.session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.account_token}',
            'Harvest-Account-Id': f'{self.account_id}',
            'User-Agent': 'Kit Hiwi'
        })

    def get_projects(self) -> List[dict]:
        params = {}
        projects = []
        next_page = 1
        while next_page is not None:
            params.update({'page': next_page})
            response = self.session.get(self.projects_url, params=params)
            data = response.json()
            projects += data['projects']
            next_page = data['next_page']

        return projects

    def get_time_entries(self, project_id: str) -> List[dict]:
        params = {
            'project_id': str(project_id)
        }
        time_entries = []
        next_page = 1
        while next_page is not None:
            params.update({'page': next_page})
            response = self.session.get(self.time_entries_url, params=params)
            data = response.json()
            time_entries += data['time_entries']
            next_page = data['next_page']

        return time_entries
