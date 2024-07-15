from requests import Session
from odoo.tools.config import config
from odoo import api, models
from .. import ellipro as EP


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
    def ellipro_get_companies(self, arguments, retry=False):
        """
        Get companies' informations for coreff
        """

        search_type = (
            EP.SearchType.ID
            if arguments["valueIsCompanyCode"]
            else EP.SearchType.NAME
        )
        request_type = EP.RequestType.SEARCH.value
        type_attribute = EP.IdType.SRC

        admin = EP.Admin(
            self.env.user.company_id.ellipro_contract,
            self.env.user.company_id.ellipro_user,
            self.env.user.company_id.ellipro_password,
        )
        main_only = str(arguments["is_head_office"]).lower()
        search_request = EP.Search(
            search_type,
            arguments["value"],
            self.env.user.company_id.ellipro_max_hits,
            type_attribute,
            main_only,
        )
        response = EP.search(admin, search_request, request_type)
        response = EP.search_response_handle(
            response
        )  # * returns all research suggestions
        return response

    @api.model
    def ellipro_get_company(self, arguments, retry=False):
        """
        ?
        """
        return

    def format_error(self, response):
        """
        Format api response
        """
        res = {}
        res["title"] = "[{}] : {}".format(
            response.status_code, response.reason
        )
        res["body"] = response.content
        return {"error": res}
