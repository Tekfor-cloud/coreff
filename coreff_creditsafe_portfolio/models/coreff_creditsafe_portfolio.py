from odoo import fields, models, api
from .. import creditsafe_portfolio as CR
from dataclasses import asdict


class CoreffCreditsafePortfolio(models.Model):
    """
    Portfolio handler for Creditsafe
    """

    _name = "coreff.creditsafe.portfolio"
    _description = "Portfolio for Creditsafe"

    name = fields.Char(required=True)
    portfolio_id = fields.Integer()

    subscriber_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="coreff_creditsafe_portfolio_subscriber_rel",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner", relation="coreff_creditsafe_portfolio_partner_rel"
    )

    def get_auth_token(self):
        settings = self.env["coreff.connector"].get_company_creditsafe_settings(
            self.env.user.id
        )
        auth_token = self.env["coreff.connector"].creditsafe_authenticate(
            settings["url"],
            settings["username"],
            settings["password"],
        )
        return auth_token

    @api.model
    def create(self, vals):
        """Extends create() to create a complete portfolio on Creditsafe API"""
        auth_token = self.get_auth_token()
        portfolio = CR.Portfolio(auth_token, portfolio_name=vals["name"])

        sub_ids = vals["subscriber_ids"][0][2]
        emails = []
        for sub_id in sub_ids:
            infos = {
                "firstName": self.env["res.partner"].browse(sub_id).name.split()[0],
                "lastName": self.env["res.partner"].browse(sub_id).name.split()[1],
                "emailAddress": self.env["res.partner"].browse(sub_id).email,
            }
            emails.append(infos)
        if emails:
            portfolio_infos = portfolio.portfolio_create(emails)
            vals["portfolio_id"] = portfolio_infos["portfolioId"]

        part_ids = vals["partner_ids"][0][2]
        company_ids = []
        for part_id in part_ids:
            id = self.env["res.partner"].browse(part_id).creditsafe_company_id
            company_ids.append(id)
        if company_ids:
            for company_id in company_ids:
                company = CR.Company(
                    auth_token, portfolio_infos["portfolioId"], company_id
                )
                company.portfolio_add_company()

        result = super(CoreffCreditsafePortfolio, self).create(vals)
        return result

    def write(self, vals):
        result = super(CoreffCreditsafePortfolio, self).write(vals)
        return result

    def unlink(self):
        """Extends unlink() to delete a complete portfolio on Creditsafe API"""
        auth_token = self.get_auth_token()
        for rec in self:
            portfolio = CR.Portfolio(auth_token, rec.portfolio_id)
            portfolio.portfolio_delete()
        result = super(CoreffCreditsafePortfolio, self).unlink()
        return result

    def sync_api(self):
        """Updates the API with local data"""
        auth_token = self.get_auth_token()
        for rec in self:
            company_ids = []
            for element in rec.partner_ids:
                id = element.creditsafe_company_id
                company_ids.append(id)
            portfolio = CR.Portfolio(auth_token, self.portfolio_id)
            creditsafe_companies = portfolio.portfolio_company_list()
            creditsafe_companies = CR.parse_company_list(creditsafe_companies)
            for company_id in company_ids:
                if company_id not in creditsafe_companies:
                    company = CR.Company(auth_token, self.portfolio_id, company_id)
                    company.portfolio_add_company()

            portfolio_infos = portfolio.get_portfolio_by_id()
            portfolio_emails = CR.parse_emails_list(portfolio_infos)
            emails = []
            for element in rec.subscriber_ids:
                email = element.email
                if email not in portfolio_emails:
                    infos = {
                        "firstName": element.name.split()[0],
                        "lastName": element.name.split()[1],
                        "emailAddress": email,
                    }
                    portfolio_infos["emails"].append(infos)
            portfolio.portfolio_update_details(
                portfolio_infos["name"], portfolio_infos["emails"]
            )

    def sync_data(self):
        # todo same as above but updating local data with the results of the api
        pass
