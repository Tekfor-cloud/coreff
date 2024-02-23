# -*- coding: utf-8 -*-
# ©2018-2019 Article714
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
from odoo import fields, models
from odoo.exceptions import UserError
from datetime import datetime


class CreditSafeDataMixin(models.AbstractModel):
    """
    Fields for creditsafe informations
    """

    _name = "coreff.creditsafe.data.mixin"
    _description = "Coreff Creditsafe Data Mixin"

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
    creditsafe_legal_form_code = fields.Char(
        string="Legal Form Code", readonly=True
    )
    creditsafe_court_registry_number = fields.Char(
        string="RCS Number", readonly=True
    )
    creditsafe_court_registry_description = fields.Char(
        string="RCS", readonly=True
    )
    creditsafe_share_capital = fields.Float(
        string="Share Capital", readonly=True
    )
    creditsafe_latest_turnover = fields.Float(
        string="Latest Turnover", readonly=True
    )
    creditsafe_incorporation_date = fields.Datetime(
        string="Registration Date", readonly=True
    )
    creditsafe_activity_code = fields.Char(
        string="Activity Code", readonly=True
    )
    creditsafe_activity_description = fields.Char(
        string="Activity Description", readonly=True
    )
    # CM: Add field for mainActivity classification
    creditsafe_activity_classification = fields.Char(
        string="Activity Classification", readonly=True
    )
    creditsafe_country = fields.Char(readonly=True)
    # CM: Add field for Year End Date
    creditsafe_yearenddate = fields.Datetime(
        string="Year End Date", readonly=True
    )
    # CM: Add field for Pre Tax Profit
    creditsafe_pretaxprofit = fields.Float(
        string="Pre Tax Profit", readonly=True
    )
    # CM: Add field for Shareholder Funds
    creditsafe_shareholderfunds = fields.Float(
        string="Shareholder Funds", readonly=True
    )
    # CM: Add field for Total Employees
    creditsafe_totalemployees = fields.Integer(
        string="Total Employees", readonly=True
    )

    # Notations
    creditsafe_status = fields.Char(string="Company Status", readonly=True)
    creditsafe_rating = fields.Integer(string="Rating", readonly=True)
    creditsafe_rating_short = fields.Char(
        string="Rating / Short Precision", readonly=True
    )
    creditsafe_rating_long = fields.Char(
        string="Rating / Long Precision", readonly=True
    )
    creditsafe_credit_limit = fields.Integer(readonly=True)
    creditsafe_contract_limit = fields.Integer(readonly=True)

    # Judgements
    creditsafe_last_judgement_date = fields.Datetime(
        string="Status Change Date", readonly=True
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

    def get_creditsafe_pdf(self):
        self.ensure_one()

        arguments = {}
        arguments["company_id"] = self.creditsafe_company_id
        arguments["user_id"] = self.env.user.id
        arguments["as_pdf"] = True
        pdf = self.env["coreff.api"].get_company(arguments)
        return pdf

    def update_creditsafe_data(self):
        """
        Update financial information
        """

        for rec in self:
            arguments = {}
            arguments["company_id"] = rec.creditsafe_company_id
            arguments["user_id"] = self.env.user.id
            company = self.env["coreff.api"].get_company(arguments)
            company = company.get("report", {})
            company_summary = company.get("companySummary", {})
            basic_information = company.get("companyIdentification", {}).get(
                "basicInformation", {}
            )
            company_address = basic_information.get("contactAddress", {})
            credit_score = company.get("creditScore", {})
            financialStatements = company.get("financialStatements", {})
            employeeInfo = company.get("otherInformation", {}).get(
                "employeesInformation", {}
            )

            rec.creditsafe_raw_data = json.dumps(company, indent=2)

            # CM: Retrieve company address details to override existing
            rec.phone = company_address.get("telephone", "")
            if len(company_address.get("houseNumber", "")) > 0:
                rec.street = (
                    company_address.get("houseNumber", "")
                    + " "
                    + company_address.get("street", "")
                )
            else:
                rec.street = company_address.get("street", "")
            rec.city = company_address.get("city", "")
            rec.zip = company_address.get("postalCode", "")
            if "zip_id" in rec._fields:
                rec.zip_id = False
            rec.state_id = self.get_state(company_address.get("province", ""))
            rec.country_id = self.get_country(
                company_address.get("country", "")
            )

            rec.creditsafe_company_name = company_summary.get(
                "businessName", ""
            )
            rec.creditsafe_legal_form = basic_information.get(
                "legalForm", {}
            ).get("description", "")
            rec.creditsafe_legal_form_code = basic_information.get(
                "legalForm", {}
            ).get("providerCode", "")
            rec.creditsafe_court_registry_number = basic_information.get(
                "companyRegistrationNumber", ""
            )
            rec.creditsafe_court_registry_description = basic_information.get(
                "commercialCourt", ""
            )
            try:
                formattedDatetime = datetime.strptime(
                    basic_information.get("companyRegistrationDate", ""),
                    "%Y-%m-%dT%H:%M:%SZ",
                )
            except Exception:
                formattedDatetime = False
            rec.creditsafe_incorporation_date = (
                formattedDatetime
                if isinstance(formattedDatetime, datetime)
                and formattedDatetime.year >= 1000
                else False
            )
            # CM: Get companySummary>mainActivity>code,description,
            # classification
            rec.creditsafe_activity_code = company_summary.get(
                "mainActivity", {}
            ).get("code", "")
            rec.creditsafe_activity_description = company_summary.get(
                "mainActivity", {}
            ).get("description", "")
            rec.creditsafe_activity_classification = company_summary.get(
                "mainActivity", {}
            ).get("classification", "")
            # CM: Get website and store on partner record
            websites = company.get("contactInformation", {}).get(
                "websites", {}
            )
            if len(websites) > 0:
                rec.website = websites[0]
            # CM: Get email and store on partner record
            emails = company.get("contactInformation", {}).get(
                "emailAddresses", {}
            )
            if len(emails) > 0:
                rec.email = emails[0]

            rec.creditsafe_country = basic_information.get("country", "")

            rec.creditsafe_status = basic_information.get(
                "companyStatus", {}
            ).get("status", "")

            # CM: Handle errors with companies that have no credit score
            try:
                rec.creditsafe_rating = (
                    credit_score.get("currentCreditRating", {})
                    .get("providerValue", {})
                    .get("value", 0)
                )
                rec.creditsafe_rating_short = credit_score.get(
                    "currentCreditRating", {}
                ).get("commonDescription", "")
                rec.creditsafe_rating_long = credit_score.get(
                    "currentCreditRating", {}
                ).get("providerDescription", "")
                rec.creditsafe_credit_limit = (
                    credit_score.get("currentCreditRating", {})
                    .get("creditLimit", {})
                    .get("value", 0)
                )
                rec.creditsafe_contract_limit = credit_score.get(
                    "currentContractLimit", {}
                ).get("value", 0)
            except:  # noqa: E722
                rec.creditsafe_rating = 0

            # CM: Format string to datetime to store in Odoo field
            try:
                formattedDatetime = datetime.strptime(
                    credit_score.get("latestRatingChangeDate", ""),
                    "%Y-%m-%dT%H:%M:%SZ",
                )
            except Exception:
                formattedDatetime = False
            rec.creditsafe_last_judgement_date = (
                formattedDatetime
                if isinstance(formattedDatetime, datetime)
                and formattedDatetime.year >= 1000
                else False
            )
            rec.creditsafe_number_of_directors = len(
                company.get("directors", {}).get("currentDirectors", {})
            )
            rec.creditsafe_last_update = fields.Datetime.now()
            rec.creditsafe_share_capital = (
                company.get("shareCapitalStructure", {})
                .get("issuedShareCapital", {})
                .get("value", 0)
            )
            # CM: Add latestTurnoverFigure field from companySummary
            rec.creditsafe_latest_turnover = company_summary.get(
                "latestTurnoverFigure", {}
            ).get("value", 0)
            # CM: Get profitBeforeTax, yearEndDate, numberOfEmployees,
            #  latestShareholdersEquityFigure
            if len(financialStatements) > 0:
                rec.creditsafe_pretaxprofit = (
                    financialStatements[0]
                    .get("profitAndLoss", {})
                    .get("profitBeforeTax", 0)
                )
                try:
                    formattedDatetime = datetime.strptime(
                        financialStatements[0].get("yearEndDate", ""),
                        "%Y-%m-%dT%H:%M:%SZ",
                    )
                except Exception:
                    formattedDatetime = False
                rec.creditsafe_yearenddate = (
                    formattedDatetime
                    if isinstance(formattedDatetime, datetime)
                    and formattedDatetime.year >= 1000
                    else False
                )
            if len(employeeInfo) > 0:
                rec.creditsafe_totalemployees = employeeInfo[0].get(
                    "numberOfEmployees", 0
                )
            rec.creditsafe_shareholderfunds = company_summary.get(
                "latestShareholdersEquityFigure", {}
            ).get("value", 0)

    def retrieve_directors_data(self):
        """
        Retrieve directors contact data for company and store
        """
        for rec in self:
            arguments = {}
            arguments["company_id"] = rec.creditsafe_company_id
            arguments["user_id"] = self.env.user.id
            company = self.env["coreff.api"].get_company(arguments)
            company = company.get("report", {})
            directors = company.get("directors", {}).get(
                "currentDirectors", {}
            )
            # CM: For each director, iterate through retrieving record
            # Next do a check for duplicates and if none present,
            # store the record as a new contact linked to this company.
            for director in directors:
                self.get_director(director)

    def get_director(self, director):
        # CM: Search for any duplicate contacts before taking action
        # - Match name and postcode
        result = self.env["res.partner"].search(
            [
                (
                    "name",
                    "ilike",
                    director.get("firstName", "")
                    + " "
                    + director.get("surname", ""),
                ),
                ("zip", "ilike", director.get("postalCode", "")),
            ]
        )
        if len(result) == 0:
            # CM: Mappings for directors to Odoo res.partner
            # Create partner contact for this director, link to parent company
            position = director.get("positions", {})[0].get("positionName", "")
            address = director.get("address", {})
            # CM: Append housenumber if exists, otherwise use street
            if len(address.get("houseNumber", "")) > 0:
                street = (
                    address.get("houseNumber", "")
                    + " "
                    + address.get("street", "")
                )
            else:
                street = address.get("street", "")
            # CM: If phone exists use it, otherwise use phone from parent
            #  company
            if len(address.get("telephone", "")) > 0:
                telephone = address.get("telephone", "")
            else:
                telephone = self.phone
            self.env["res.partner"].create(
                {
                    "name": director.get("firstName", "")
                    + " "
                    + director.get("surname", ""),
                    "parent_id": self.id,
                    "company_type": "person",
                    "function": position,
                    "ref": director.get("id", ""),
                    "street": street,
                    "city": address.get("city", ""),
                    "zip": address.get("postalCode", ""),
                    "phone": telephone,
                    "type": "other",
                    "title": self.get_title(director.get("title", "")),
                    "state_id": self.get_state(address.get("province", "")),
                    "country_id": self.get_country(address.get("country", "")),
                }
            )
            return True

    def get_title(self, title):
        # CM: Search for res.partner.title that matches the submitted string
        #  with a dot added
        if len(title) > 0:
            result = self.env["res.partner.title"].search(
                [
                    "|",
                    ("shortcut", "=", title),
                    ("shortcut", "ilike", title + "."),
                ]
            )
            return result.id
        else:
            return False

    def get_state(self, state):
        # CM: Search for res.country that matches the submitted string
        if len(state) > 0:
            result = self.env["res.country.state"].search(
                [("name", "=", state)]
            )
            return result.id
        else:
            return False

    def get_country(self, country_code):
        # CM: Search for res.country.state that matches the submitted string
        # If no match found, use country of parent company
        if len(country_code) > 0:
            result = self.env["res.country"].search(
                [("code", "=", country_code)]
            )
            return result.id
        else:
            return self.country_id.id
