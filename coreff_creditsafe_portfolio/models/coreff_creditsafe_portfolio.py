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

    def portfolio_auth(self):
        settings = self.env["coreff.connector"].get_company_creditsafe_settings(
            self.env.user.id
        )
        auth_key = self.env["coreff.connector"].creditsafe_authenticate(
            settings["url"],
            settings["username"],
            settings["password"],
        )
        return auth_key

    @api.model
    def create(self, vals):
        """Extends create() to create a complete portfolio on Creditsafe API"""
        auth_key = self.portfolio_auth()
        portfolio = CR.Portfolio(auth_key, portfolio_name=vals["name"])

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
                    auth_key, portfolio_infos["portfolioId"], company_id
                )
                company.portfolio_add_company()

        result = super(CoreffCreditsafePortfolio, self).create(vals)
        return result

    def write(self, vals):
        result = super(CoreffCreditsafePortfolio, self).write(vals)
        return result

    def unlink(self):
        """Extends unlink() to delete a complete portfolio on Creditsafe API"""
        auth_key = self.portfolio_auth()
        for rec in self:
            portfolio = CR.Portfolio(auth_key, rec.portfolio_id)
            portfolio.portfolio_delete()
        result = super(CoreffCreditsafePortfolio, self).unlink()
        return result
