from requests import Session
from odoo.tools.config import config
from odoo import api, models
from .. import axesor as AX



class CustomSessionProxy(Session):
    def __init__(self):
        super().__init__()

        proxy_http = config.get("proxy_http")
        proxy_https = config.get("proxy_https")

        self.proxies = {
            "http": proxy_http,
            "https": proxy_https,
        }


class CoreffConnector(models.Model):
    _inherit = "coreff.connector"

    @api.model
    def axesor_get_companies(self, arguments, retry=False):
        """
        Get companies' informations for coreff
        """
        user = self.env.user.company_id.axesor_login
        password = self.env.user.company_id.axesor_password
        search_value = arguments["value"]
        if arguments["valueIsCompanyCode"]:
            response = AX.search_by_code(user, password, search_value)
        else:
            response = AX.search_by_name(user, password, search_value)
        return response

    @api.model
    def axesor_get_company(self, arguments, retry=False):
        """
        ?
        """
        return

    def axesor_format_error(self, response):
        """
        Format api response
        """
        res = {}
        res["title"] = "[{}] : {}".format(
            response.status_code, response.reason
        )
        res["body"] = response.content
        return {"error": res}
