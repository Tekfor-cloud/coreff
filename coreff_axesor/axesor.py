import requests
import pprint
from odoo.exceptions import Exception

URL_MAPPING = {
    "sandbox":"https://apis.axesor.es/sandbox/Qualitas/v1",
    "production":"https://apis.axesor.es/Qualitas/v1"
}

def get_token(url_type, login, password):
    token_url = f"{URL_MAPPING[url_type]}/authorization?userName={login}&pwd={password}"
    token = requests.get(token_url).json()["token"]
    return token


def search(url_type, token, query):
    url = URL_MAPPING[url_type] + "/CompanySearch"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers, params=query)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.text)
    return search_parse(response.json())


def search_parse(response):
    companies = response["CompanySeachResponse"]["Companies"]
    # companies = response["CompanySearchResponse"]["Companies"] # TO REPLACE UPON API FIX (api-side typo)
    companies_infos = []
    if type(companies) != list:
        companies = [companies]
    for company in companies:
        company_infos = {}
        company_infos["coreff_company_code"] = company["Company"]["TIN"]
        company_infos["name"] = company["Company"]["CorporateName"]
        company_infos["axesor_internal_id"] = company["Company"]["InfotelCode"]
        companies_infos.append(company_infos)
    return companies_infos


def search_by_name(url_type, token, company_name):
    query = {"name": company_name}
    response = search(url_type, token, query)
    return response


def search_by_code(url_type, token, code):
    query = {"tin": code}
    response = search(url_type, token, query)
    return response


def get_directors(url_type, token, code):
    query = {"tin": code}
    url = URL_MAPPING[url_type] + "/ShareholdersCorporateBodiesInfo"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers, params=query)
    if response.status_code != 200:
        raise Exception(response.text)
    response = response.json()
    directors = []
    for shareholder in response["ShareholdersCorporateBodiesInfoResponse"]["ShareholdersList"]:
        director = {}
        director["name"] = shareholder["Shareholder"]["Name"]
        director["job"] = "Shareholder"
        directors.append()
    for corporate in response["CorporateBodiesInManagementPositionsList"]["CorporateBody"]:
        director["name"] = corporate["Name"]
        director["job"] = "Corporate Body"
        directors.append()
    return directors


def get_infos(url_type, token, code):
    query = {"tin": code, "retrieveRiskScoringAndPaymentData": True}
    url = URL_MAPPING[url_type] + "/CompanyEnrichment"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers, params=query)
    if response.status_code != 200:
        raise Exception(response.text)
    response = response.json()
    response = response["CompanyEnrichmentResponse"]["Company"]
    company = {}
    company["dict"] = response
    company["pretty_json"] = pprint.pformat(response)
    return company
