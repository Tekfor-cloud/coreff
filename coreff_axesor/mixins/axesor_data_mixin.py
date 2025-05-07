from odoo import fields, models, _
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
        endpoint = self.env.user.company_id.axesor_endpoint
        api_token = AX.get_token(endpoint, self.env.user.company_id.axesor_login, self.env.user.company_id.axesor_password)
        for rec in self:
            if len(rec.coreff_company_code) != 14:
                raise Exception(
                    _(
                        "Please replace the SIREN code for a SIRET one. To proceed, you can just add a 0 at the end of the SIREN number to get all different SIRET numbers."
                    )
                )
            directors = AX.get_directors(
                endpoint,
                api_token,
                rec.coreff_company_code,
            )
            for director in directors:
                self.env["res.partner"].create(
                    {
                        "name": director["name"],
                        "parent_id": self.id,
                        "company_type": "person",
                        "function": director["job"],
                        "type": "other",
                    }
                )

    def axesor_get_infos(self):
        endpoint = self.env.user.company_id.axesor_endpoint
        api_token = AX.get_token(endpoint, self.env.user.company_id.axesor_login, self.env.user.company_id.axesor_password)
        for rec in self:
            infos = AX.get_infos(
                endpoint,
                api_token,
                rec.coreff_company_code,
            )
            rec.street = infos["dict"]["CompleteAddress"]
            rec.city = infos["dict"]["Town"]
            rec.zip = infos["dict"]["PostCode"]
            country_alpha3 = infos["dict"]["AddressNormalisation"]["Country"]["Code"]
            country_code = pycountry.countries.search_fuzzy(country_alpha3)[0].alpha_2
            cr = self.env.cr
            cr.execute(f"select id from res_country where code = '{country_code}' limit 1")
            self.country_id = cr.fetchone()
            rec.phone = infos["dict"]["Phone"]
            rec.website = infos["dict"]["Web"]
            rec.axesor_risk_score = infos["dict"]["RiskScoring"]
            rec.axesor_data = infos["pretty_json"]
            
    def axesor_get_report(self):
        for rec in self:
            return

    