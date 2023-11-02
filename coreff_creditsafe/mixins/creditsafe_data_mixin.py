# -*- coding: utf-8 -*-
# ©2018-2019 Article714
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
from odoo import fields, models
from odoo.exceptions import UserError


class CreditSafeDataMixin(models.AbstractModel):
    """
    Fields for creditsafe informations
    """

    _name = "coreff.creditsafe.data.mixin"

    creditsafe_visibility = fields.Boolean(
        compute="_compute_creditsafe_visibility",
        default=lambda rec: rec._default_creditsafe_visibility(),
    )

    creditsafe_company_id = fields.Char(string="Creditsafe id")

    creditsafe_raw_data = fields.Text(string="Raw Data", readonly=True)

    # Identification
    creditsafe_company_name = fields.Char(
        string="Business Name", readonly=True
    )
    creditsafe_legal_form = fields.Char(string="Legal Form", readonly=True)
    creditsafe_court_registry_number = fields.Char(
        string="RCS Number", readonly=True
    )
    creditsafe_court_registry_description = fields.Char(
        string="RCS", readonly=True
    )
    creditsafe_share_capital = fields.Float(
        string="Share Capital", readonly=True
    )
    creditsafe_incorporation_date = fields.Date(
        string="Registration Date", readonly=True
    )
    creditsafe_activity_code = fields.Char(
        string="Activity Code", readonly=True
    )
    creditsafe_activity_description = fields.Char(
        string="Activity Description", readonly=True
    )
    creditsafe_country = fields.Char(string="Country", readonly=True)

    # Notations
    creditsafe_status = fields.Char(string="Status", readonly=True)
    creditsafe_rating = fields.Char(string="Rating", readonly=True)
    creditsafe_rating_short = fields.Char(
        string="Rating / Short Precision", readonly=True
    )
    creditsafe_rating_long = fields.Char(
        string="Rating / Long Precision", readonly=True
    )
    creditsafe_credit_limit = fields.Float(
        string="Credit Limit", readonly=True
    )

    # Judgements
    creditsafe_last_judgement_date = fields.Date(
        string="Last Judgement", readonly=True
    )
    creditsafe_last_ccj_date = fields.Date(string="", readonly=True)
    creditsafe_number_of_directors = fields.Char(
        string="Number of Directors", readonly=True
    )

    creditsafe_last_update = fields.Datetime(
        readonly=True, string="Last Update"
    )

    def _compute_creditsafe_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            if company.coreff_connector_id == self.env.ref(
                "coreff_creditsafe.coreff_connector_creditsafe_api"
            ):
                rec.creditsafe_visibility = True
            else:
                rec.creditsafe_visibility = False

    def _default_creditsafe_visibility(self):
        company = self.env.user.company_id
        if company.coreff_connector_id == self.env.ref(
            "coreff_creditsafe.coreff_connector_creditsafe_api"
        ):
            return True
        else:
            return False

    def _clean_creditsafe_dates(self, data):
        field_names = [
            name
            for name, field in self._fields.items()
            if name.startswith("creditsafe_") and field.type == "date"
        ]
        for key in field_names:
            if data.get(key) == "0001-01-01T00:00:00Z":
                data[key] = False

    def update_creditsafe_data(self):
        """
        Update financial information
        """
        for rec in self:
            rec.write(rec.get_creditsafe_data())

    def get_creditsafe_pdf(self):
        self.ensure_one()

        arguments = {}
        arguments["company_id"] = self.creditsafe_company_id
        arguments["user_id"] = self.env.user.id
        arguments["as_pdf"] = True
        pdf = self.env["coreff.api"].get_company(arguments)
        return pdf

    def get_creditsafe_data(self):
        self.ensure_one()

        arguments = {}
        arguments["company_id"] = self.creditsafe_company_id
        arguments["user_id"] = self.env.user.id
        arguments["as_pdf"] = False
        company = self.env["coreff.api"].get_company(arguments)

        if "error" in company:
            raise UserError(company["error"]["body"])

        company = company.get("report", {})
        company_summary = company.get("companySummary", {})
        basic_information = company.get("companyIdentification", {}).get(
            "basicInformation", {}
        )
        credit_score = company.get("creditScore", {})
        provider_value = credit_score.get("currentCreditRating", {}).get(
            "providerValue", {}
        )

        try:
            creditsafe_share_capital = float(
                company.get("shareCapitalStructure", {})
                .get("nominalShareCapital", {})
                .get("value", 0)
            )
        except ValueError:
            creditsafe_share_capital = 0

        try:
            creditsafe_credit_limit = float(
                credit_score.get("currentCreditRating", {})
                .get("creditLimit", {})
                .get("value", 0)
            )
        except ValueError:
            creditsafe_credit_limit = 0

        data = {
            "creditsafe_raw_data": json.dumps(company, indent=2),
            "creditsafe_company_name": company_summary.get("businessName", ""),
            "creditsafe_legal_form": basic_information.get(
                "legalForm", {}
            ).get("description", ""),
            "creditsafe_court_registry_number": basic_information.get(
                "companyRegistrationNumber", ""
            ),
            "creditsafe_court_registry_description": basic_information.get(
                "commercialCourt", ""
            ),
            "creditsafe_incorporation_date": basic_information.get(
                "companyRegistrationDate", ""
            )
            or False,
            "creditsafe_activity_code": basic_information.get(
                "principalActivity", {}
            ).get("code", ""),
            "creditsafe_activity_description": basic_information.get(
                "principalActivity", {}
            ).get("description", ""),
            "creditsafe_country": basic_information.get("country", ""),
            "creditsafe_status": basic_information.get(
                "companyStatus", {}
            ).get("status", ""),
            "creditsafe_rating": f"{provider_value.get('value')} "
            f"/ {provider_value.get('maxValue')}",
            "creditsafe_rating_short": credit_score.get(
                "currentCreditRating", {}
            ).get("commonDescription", ""),
            "creditsafe_rating_long": credit_score.get(
                "currentCreditRating", {}
            ).get("providerDescription", ""),
            "creditsafe_credit_limit": creditsafe_credit_limit,
            "creditsafe_last_judgement_date": credit_score.get(
                "latestRatingChangeDate", ""
            )
            or False,
            "creditsafe_number_of_directors": len(
                company.get("directors", {}).get("currentDirectors", {})
            ),
            "creditsafe_last_update": fields.Datetime.now(),
            "creditsafe_share_capital": creditsafe_share_capital,
        }
        self._clean_creditsafe_dates(data)
        return data
