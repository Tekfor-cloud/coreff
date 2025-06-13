# -*- coding: utf-8 -*-
# ©2018-2019 Article714
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from zeep import Client
from odoo.tools.config import config
from odoo import api, models


class CoreffConnector(models.Model):
    _inherit = "coreff.connector"

    @staticmethod
    def set_proxies_on_client(client):

        proxy_http = config.get("proxy_http")
        proxy_https = config.get("proxy_https")

        client.transport.session.proxies = {
            "http": proxy_http,
            "https": proxy_https,
        }

    @api.model
    def informa_get_companies(self, arguments):
        """
        Get companies
        """
        settings = self.get_company_informa_settings(arguments["user_id"])
        client = Client(
            settings["url"]
            + "/DNB_WebServices.Providers.LookUp_V3:wsp_LookUp_V3?WSDL"
        )
        self.set_proxies_on_client(client)

        look_up_input = {}
        look_up_input["Country_Code"] = settings["country_code"]

        look_up_input["Name"] = arguments["value"]

        look_up_request = {}
        look_up_request["UserId"] = settings["username"]
        look_up_request["Password"] = settings["password"]
        look_up_request["lookUpInput"] = look_up_input

        result = client.service.ws_LookUp(look_up_request)["CREDITMSGSRSV2"]
        if not result:
            return []
        result = result["LOOKUPTRNRS"]
        if not result:
            return []
        result = result["LOOKUPRS"]
        if not result:
            return []
        result = result["LOOKUPRSCOMPANY"]
        if not result:
            return []
        companies = result["ArrayOfLOOKUPRSCOMPANYItem"]
        if not companies:
            return []
        companies.sort(key=lambda x: (x["NME"], x["NON_POST_TOWN"]))
        suggestions = []
        for company in companies:
            suggestion = {}
            suggestion["informa_company_id"] = company["DUNS_NBR"]
            suggestion["coreff_company_id_key"] = "informa_company_id"
            suggestion["name"] = company["NME"]
            suggestion["street"] = company["ADR_LINE"]
            suggestion["city"] = company["NON_POST_TOWN"]
            suggestion["zip"] = company["POST_CODE"]
            suggestion["phone"] = company["TLCM_NBR"]
            suggestions.append(suggestion)
        return suggestions

    @api.model
    def informa_get_company(self, arguments):
        """
        Get company
        """
        settings = self.get_company_informa_settings(arguments["user_id"])
        client = Client(
            settings["url"]
            + "/DNB_WebServices.Providers.OrderAndInvestigations.GDP_V4"
            ":wsp_GDP_V4?WSDL"
        )
        self.set_proxies_on_client(client)

        orders = {}
        orders["User_Language"] = "EN"
        orders["DnB_DUNS_Number"] = arguments["company_id"]
        orders["Country_Code"] = settings["country_code"]
        orders["Product"] = "Decision Support "
        orders["Product_Type"] = "D"

        immediate_delivery = {}
        immediate_delivery["Mode"] = "DIRECT"
        immediate_delivery["Format"] = "XML"

        gdp_request = {}
        gdp_request["UserId"] = settings["username"]
        gdp_request["Password"] = settings["password"]
        gdp_request["Orders"] = orders
        gdp_request["Immediate_Delivery"] = immediate_delivery

        result = client.service.ws_OtherGDPProducts(gdp_request)[
            "CREDITMSGSRSV2"
        ]
        if not result:
            return {}
        result = result["DATATRNRS"]
        if not result:
            return {}
        result = result["DATARS"]
        if not result:
            return {}
        return result

    def get_company_informa_settings(self, user_id):
        """
        Get company settings for Informa
        """
        res = {}
        user = self.env["res.users"].browse(user_id)
        company = user.company_id
        res["url"] = company.get_parent_informa_field("informa_url")
        res["username"] = company.get_parent_informa_field("informa_username")
        res["password"] = company.get_parent_informa_field("informa_password")
        res["country_code"] = company.informa_country_code
        return res
