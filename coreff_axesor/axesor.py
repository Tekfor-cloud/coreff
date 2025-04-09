import requests
import base64
from dataclasses import dataclass
import logging

URL_API = "https://apis.axesor.es/sandbox/Qualitas/v1/"

def get_token(login, password):
    token_url = f"https://apis.axesor.es/sandbox/qualitas/v1/authorization?userName={login}&pwd={password}"
    token = requests.get(token_url).json()["token"]
    return token

def search(token, query):
    url = URL_API + "CompanySearch"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers, params=query).json()
    return search_parse(response)
    
def search_parse(response):
    companies = response["CompanySeachResponse"]["Companies"]
    # companies = response["CompanySearchResponse"]["Companies"] # TO REPLACE UPON API FIX (server-side typo)
    companies_infos = []
    for company in companies:
        company_infos = {}
        company_infos["vat"] = company["Company"]["TIN"]
        company_infos["name"] = company["Company"]["CorporateName"]
        company_infos["infotel_code"] = company["Company"]["InfotelCode"]
        companies_infos.append(company_infos)
    return companies_infos

def search_by_name(token, company_name, login, password):
    token = get_token(login, password)
    query = {"name": company_name}
    response = search(token, query) 
    return response
    
def search_by_code(token, code):
    query = {"tin": code}
    response = search(token, query)
    return response
    
def get_directors(token, code):
    query = {"tin":code}
    url = URL_API + "ShareholdersCorporateBodiesInfo"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers, params=query).json()
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
    
def get_infos(token, code):
    #$ retrieveRiskScoringAndPaymentData
    #* return as a string 
    query = {"tin": code}
    url = URL_API + "CompanyEnrichment"
    headers = {"Authorization": "Bearer " + token}
    return requests.get(url, headers=headers, params=query).json()
    #todo parse response
    #infos = {'CompanyEnrichmentResponse': {'Company': {'CorporateName': 'AXESOR CONOCER PARA DECIDIR SA', 'TIN': 'A18413302', 'InfotelCode': '987857', 'Employees': '145', 'Sales': '4205095.00', 'CNAE': '6311 - Proceso de datos, hosting y actividades relacionadas', 'CNAECode': '6311', 'CNAEDescription': 'Proceso de datos, hosting y actividades relacionadas', 'CompanyAge': '26', 'Delegations': '3', 'RiskScoring': '11', 'ActivityLevel': '9', 'Exports': '1', 'SocialCapital': '272500.00', 'PaymentTerm': '180', 'Web': 'www.axesor.es', 'Sector': '10', 'Active': '1', 'CompleteAddress': 'C/ GRAHAM BELL, Nº 1, POL. IND. SAN ISIDRO, EDIFICIO EXPERIAN', 'PostCode': '18100', 'Province': 'GRANADA', 'Town': 'ARMILLA', 'INECodeTown': '18021', 'INECodeStreet': '00825', 'Phone': '958011480', 'ContactPerson': 'DIONISIO TORRE RAMOS', 'PositionContactPerson': 'DIRECTOR GENERAL', 'Status': '1 - Activa', 'SocialForm': 'SOCIEDAD ANONIMA', 'SocialFormCode': '1', 'DateRevenue': '2021', 'ConstitutionDate': 'May 20 1996 12:00AM', 'StatusCode': '1', 'AddressNormalisation': {'Country': {'Code': 'ESP', 'Name': 'ESPAÑA'}, 'Province': {'ProvinceId': '18', 'NormalisedName': 'GRANADA'}, 'Town': {'TownId': '21', 'NormalisedName': 'ARMILLA'}, 'Locality': {'LocalityId': '170101', 'NormalisedName': 'ARMILLA'}, 'Via': {'StreetCode': '327513', 'StreetIdentified': 'SI', 'PostCode': '18100', 'NormalisedName': 'GRAHAM BELL', 'StreetType': 'CALLE', 'StreetTypeCode': '31', 'BuildingNumber': '1', 'RestOfAddress': 'POL. IND. SAN ISIDRO, EDIFICIO EXPERIAN'}, 'Geolocation': {'Latitude': '37.1553264800', 'Longitude': '-3.6124306400'}}}}}
    
def get_report(token, code):
    #* ???
    pass
