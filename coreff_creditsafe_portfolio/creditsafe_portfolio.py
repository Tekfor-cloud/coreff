import requests
import json
from dataclasses import dataclass, field, asdict
import logging


@dataclass
class Portfolio:
    auth_token: str
    portfolio_id: str = ""
    portfolio_name: str = ""
    headers: float = field(init=False)
    url = "https://connect.creditsafe.com/v1/monitoring/portfolios"

    def __post_init__(self):
        self.headers = {"Authorization": "Bearer " + self.auth_token}

    def portfolio_create(self, emails, frequency="1"):
        payload = {
            "name": self.portfolio_name,
            "emails": emails,
            "emailSubject": "Creditsafe Monitoring Notification on portfolio {{portfolioName}}",
            "emailLanguage": "fr",
            "frequency": frequency,
        }
        logging.info(payload)
        response = requests.post(self.url, json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()

    def portfolio_delete(self):
        response = requests.delete(
            f"{self.url}/{self.portfolio_id}", headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()

    def get_portfolio_by_id(self):
        response = requests.get(f"{self.url}/{self.portfolio_id}", headers=self.headers)
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()


@dataclass
class Company:
    auth_token: str
    portfolio_id: str
    company_id: str = ""
    headers: float = field(init=False)
    url: float = field(init=False)

    def __post_init__(self):
        self.headers = {"Authorization": "Bearer " + self.auth_token}
        self.url = f"https://connect.creditsafe.com/v1/monitoring/portfolios/{self.portfolio_id}/companies"

    def portfolio_add_company(self, reference="", text="", limit=""):
        payload = {
            "id": self.company_id,
            "personalReference": reference,
            "freeText": text,
            "personalLimit": limit,
        }
        response = requests.post(self.url, json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()

    def portfolio_company_list(self):
        response = requests.get(self.url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()

    def portfolio_company_delete(self):
        response = requests.get(f"{self.url}/{self.company_id}", headers=self.headers)
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()

    def portfolio_company_clear(self):
        query = {"clearAll": "true"}
        payload = {"companies": []}
        response = requests.patch(
            f"{self.url}/clear", json=payload, headers=self.headers, params=query
        )
        if response.status_code != 200:
            raise Exception(response.content)
        return response.json()

    def portfolio_company_update(self, reference="", text="", limit=""):
        payload = {
            "personalReference": reference,
            "freeText": text,
            "personalLimit": limit,
        }
        response = requests.post(
            f"{self.url}/{self.company_id}", json=payload, headers=self.headers
        )
        if response.status_code != 200 and response.status_code != 204:
            raise Exception(response.content)
        return response.json()
