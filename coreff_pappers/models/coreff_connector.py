from requests import Session
from odoo.tools.config import config
from odoo import api, models
from .. import pappers as PA


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
    def pappers_get_companies(self, arguments, retry=False):
        """
        Get companies' informations for coreff
        """

        search_value = arguments["value"]
        api_token = self.env.user.company_id.pappers_api_token
        if arguments["valueIsCompanyCode"]:
            response = PA.search_code(
                api_token, search_value, arguments["is_head_office"]
            )
            return response
        else:
            response = PA.search_name(
                api_token, search_value, arguments["is_head_office"]
            )
        return response

    @api.model
    def pappers_get_company(self, arguments, retry=False):
        """
        ?
        """
        return

    def pappers_format_error(self, response):
        """
        Format api response
        """
        res = {}
        res["title"] = "[{}] : {}".format(response.status_code, response.reason)
        res["body"] = response.content
        return {"error": res}
