from odoo import fields, models, _
from odoo.tools.config import config
from .. import axesor as AX
import pycountry


class AxesorDataMixin(models.AbstractModel):
    """
    Fields for axesor informations
    """

    _name = "coreff.axesor.data.mixin"
    _description = "Coreff Axesor Data Mixin"

    axesor_visibility = fields.Boolean(compute="_compute_axesor_visibility")

    axesor_internal_id = fields.Char()
    axesor_risk_score = fields.Text()
    axesor_data = fields.Text()

    def _compute_axesor_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            rec.axesor_visibility = (
                company.coreff_connector_id
                == self.env.ref("coreff_axesor.coreff_connector_axesor_api")
            )

    def axesor_retrieve_directors(self):
        """Create new partners linked to the company."""
        for rec in self:
            return

    def axesor_get_infos(self):
        """Fetch the company's infos from the API using company code"""
        proxies = {
            "http":config.get("proxy_http"),
            "https":config.get("proxy_https"),
        }
        for rec in self:
            login = self.env.user.company_id.axesor_login
            password = self.env.user.company_id.axesor_password
            infos = AX.get_infos(login, password, rec.coreff_company_code, proxies)
            rec.street = infos["street"]
            rec.city = infos["city"]
            rec.zip = infos["zip"]
            country_name = infos["country"]
            country_code = pycountry.countries.search_fuzzy(country_name)[0].alpha_2
            cr = self.env.cr
            cr.execute(f"select id from res_country where code = '{country_code}' limit 1")
            self.country_id = cr.fetchone()
            rec.phone = infos["phone"]
            rec.website = infos["website"]
            rec.email = infos["email"]
            rec.vat = infos["tax_id"]
            rec.axesor_risk_score = infos["axesor_risk_score"]
            rec.axesor_data = infos["axesor_data"]

    def axesor_get_report(self):
        for rec in self:
            return

    