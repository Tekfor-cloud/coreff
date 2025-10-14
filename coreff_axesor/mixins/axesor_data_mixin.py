from odoo import fields, models, _
from odoo.exceptions import ValidationError
from .. import axesor as AX
import requests
from datetime import datetime


class AxesorDataMixin(models.AbstractModel):
    """
    Fields for axesor informations
    """

    _name = "coreff.axesor.data.mixin"
    _description = "Coreff Axesor Data Mixin"

    axesor_visibility = fields.Boolean(compute="_compute_axesor_visibility")

    axesor_internal_id = fields.Char()
    axesor_write_date = fields.Datetime()
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
        session = self.get_session()
        for rec in self:
            if len(rec.coreff_company_code) < 9:
                raise ValidationError(
                    "The company code must be contain at least 9 caracters."
                )
            login = self.env.user.company_id.axesor_login
            password = self.env.user.company_id.axesor_password
            infos = AX.get_infos(
                login, password, rec.coreff_company_code, session
            )

            # Compatibility with base_location module : https://github.com/OCA/partner-contact/tree/16.0/base_location
            if "zip_id" in rec._fields:
                rec.zip_id = False

            rec.street = infos["street"]
            rec.city = infos["city"]
            rec.zip = infos["zip"]
            rec.phone = infos["phone"]
            rec.website = infos["website"]
            rec.email = infos["email"]
            rec.vat = infos["tax_id"]
            rec.axesor_risk_score = infos["axesor_risk_score"]
            rec.axesor_data = infos["axesor_data"]
            rec.axesor_internal_id = infos["internal_id"]
            state = infos["state"]
            rec.state_id = (
                self.env["res.country.state"].search(
                    [("name", "ilike", state)], limit=1
                )
                if state
                else False
            )
            rec.country_id = self.env.ref("base.es")
            rec.coreff_activity_code = infos["cnae"]
            rec.axesor_write_date = datetime.now()

    def axesor_get_report(self):
        session = self.get_session()
        for rec in self:
            if len(rec.coreff_company_code) < 9:
                raise ValidationError(
                    "The company code must be contain at least 9 caracters."
                )
            login = self.env.user.company_id.axesor_login
            password = self.env.user.company_id.axesor_password
            pdf = AX.get_infos_pdf(
                login, password, rec.coreff_company_code, session
            )
            import logging

            logging.info(pdf)

    def get_session(self):
        return requests.Session()
