import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum


class IdType(Enum):
    REGISTER = "register"
    SRC = "src"
    ESTB = "register-estb"
    VAT = "vat"


class SearchType(Enum):
    ID = 0
    NAME = 1


class RequestType(Enum):
    SEARCH = "svcSearch"
    ONLINEORDER = "svcOnlineOrder"
    CATALOGUE = "svcCatalogue"


@dataclass
class Admin:
    contract_id: str
    user_id: str
    password: str

    def set_element(self, root):
        admin = ET.SubElement(root, "admin")
        client = ET.SubElement(admin, "client")
        context = ET.SubElement(admin, "context")
        ET.SubElement(client, "contractId").text = self.contract_id
        ET.SubElement(client, "userId").text = self.user_id
        ET.SubElement(client, "password").text = self.password
        ET.SubElement(context, "appId", attrib={"version": "1"}).text = (
            "WSRISK"
        )
        ET.SubElement(context, "date").text = "2013-11-05T17:38:15+01:00"


@dataclass
class Search:
    search_type: SearchType
    search_text: str
    max_hits: str
    type_attribute: IdType
    main_only: str
    custom_content = "false"
    company_status = "active"
    establishment_status = "active"
    phonetic_search = "false"

    def set_element(self, root):
        request = ET.SubElement(root, "request")

        search_criteria = ET.SubElement(request, "searchCriteria")
        if self.search_type == SearchType.ID:
            ET.SubElement(
                search_criteria,
                "id",
                attrib={"type": self.type_attribute.value},
            ).text = self.search_text
        elif self.search_type == SearchType.NAME:
            ET.SubElement(search_criteria, "name").text = self.search_text
        address = ET.SubElement(search_criteria, "address")
        ET.SubElement(address, "country", attrib={"code": "FRA"})

        search_options = ET.SubElement(request, "searchOptions")
        ET.SubElement(search_options, "phoneticSearch").text = (
            self.phonetic_search
        )
        ET.SubElement(search_options, "maxHits").text = self.max_hits
        ET.SubElement(search_options, "mainOnly").text = self.main_only
        ET.SubElement(search_options, "customContent").text = (
            self.custom_content
        )
        ET.SubElement(search_options, "companyStatus").text = (
            self.company_status
        )
        ET.SubElement(search_options, "establishmentStatus").text = (
            self.establishment_status
        )


@dataclass
class Order:
    company_id: str
    product_id: str
    product_version = "1"
    output_method = "raw"
    format = "XML"

    def set_element(self, root):
        request = ET.SubElement(root, "request")
        ET.SubElement(request, "country", attrib={"code": "FRA"})
        ET.SubElement(request, "id", attrib={"type": "src"}).text = (
            self.company_id
        )
        ET.SubElement(
            request,
            "product",
            attrib={"range": self.product_id, "version": self.product_version},
        )
        delivery_options = ET.SubElement(request, "deliveryOptions")
        ET.SubElement(delivery_options, "outputMethod").text = (
            self.output_method
        )
        ET.SubElement(delivery_options, "format").text = self.format


@dataclass
class Catalogue:
    company_id: str
    country_code = "FRA"

    def set_element(self, root):
        request = ET.SubElement(root, "request")
        ET.SubElement(request, "country", attrib={"code": self.country_code})
        ET.SubElement(request, "id", attrib={"type": "src"}).text = (
            self.company_id
        )


def search(admin, request, request_type, lang="FR", version="2.2"):
    """Send XML request to Ellipro and return an elementTree object."""
    headers = {"Content-Type": "application/xml"}
    root = ET.Element(
        f"{request_type}Request", attrib={"lang": lang, "version": version}
    )
    admin.set_element(root)
    request.set_element(root)
    body = ET.tostring(root)

    request_result = requests.post(
        f"https://services-test.data-access-gateway.com/1/rest/{request_type}",
        data=body,
        headers=headers,
    )
    return ET.fromstring(request_result.text)


def search_response_handle(response):
    """Parse a SvcSearch request response and return a list of dictionaries."""
    suggestions = []
    for establishment in response.iter("establishment"):
        suggestion = {}
        suggestion["name"] = establishment.findall("name")[0].text
        suggestion["coreff_company_code"] = establishment.findall(
            "id[@idName='SIREN']"
        )[0].text
        suggestion["ellipro_siren"] = establishment.findall(
            "id[@idName='SIREN']"
        )[0].text
        suggestion["ellipro_siret"] = establishment.findall(
            "id[@idName='SIRET']"
        )[0].text
        suggestion["ellipro_identifiant_interne"] = establishment.findall(
            "id[@idName='Identifiant interne']"
        )[0].text
        if establishment.findall("communication[@type='phone']") != []:
            suggestion["phone"] = establishment.findall(
                "communication[@type='phone']"
            )[0].text
        suggestion["city"] = establishment.findall("address/cityName")[0].text
        suggestion["zip"] = establishment.findall("address/cityCode")[0].text
        suggestion["street"] = establishment.findall("address/addressLine")[
            0
        ].text
        if establishment.findall("name[@type='businessname']") != []:
            suggestion["ellipro_business_name"] = establishment.findall(
                "name[@type='businessname']"
            )[0].text
        if establishment.findall("name[@type='tradename']") != []:
            suggestion["ellipro_trade_name"] = establishment.findall(
                "name[@type='tradename']"
            )[0].text
        suggestion["ellipro_city"] = establishment.findall("address/cityName")[
            0
        ].text
        suggestion["ellipro_zipcode"] = establishment.findall(
            "address/cityCode"
        )[0].text
        suggestion["ellipro_street_address"] = establishment.findall(
            "address/addressLine"
        )[0].text
        if establishment.findall("communication[@type='phone']") != []:
            suggestion["ellipro_phone_number"] = establishment.findall(
                "communication[@type='phone']"
            )[0].text
        suggestions.append(suggestion)
    return suggestions


def parse_order(order):
    """Parse a SvcOnlineOrder request response and return a dictionary."""
    parsed_order = {}
    for response in order.findall("response"):
        name = response.findall("intlReport/header/report/reportId")[0].text
        price = (
            response.findall("intlReport/header/report/defaultCurrencyUnit")[
                0
            ].text
            + " "
            + response.findall("intlReport/header/report/defaultCurrency")[
                0
            ].text
        )
        parsed_order["ellipro_order_result"] = (
            name + " pour le prix de " + price
        )
        parsed_order["ellipro_rating_score"] = (
            int(
                response.findall(
                    "intlReport/assessmentData/score/value[@type='score']"
                )[0].text
            )
            * 10
        )  # * rating goes from 0 to 10, rating*10 for % value
        rating_riskclass = response.findall(
            "intlReport/assessmentData/score/value[@type='riskclass']"
        )[0].text
        parsed_order["ellipro_rating_riskclass"] = (
            (4 - (ord(rating_riskclass) - 65)) / 4 * 100
        )  # * letter given goes from A for best to E for worst, converted to 0-4 scale then to %
    return parsed_order
