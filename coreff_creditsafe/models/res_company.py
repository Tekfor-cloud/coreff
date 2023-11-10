# ©2018-2019 Article714
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    creditsafe_visibility = fields.Boolean(
        compute="_compute_creditsafe_visibility", default=False
    )

    creditsafe_use_parent_company = fields.Boolean(default=False)

    creditsafe_url = fields.Char()
    creditsafe_username = fields.Char()
    creditsafe_password = fields.Char()
    creditsafe_language = fields.Char(default="en")

    creditsafe_parent_url = fields.Char(
        compute="_compute_creditsafe_parent_url"
    )
    creditsafe_parent_username = fields.Char(
        compute="_compute_creditsafe_parent_username"
    )
    creditsafe_parent_password = fields.Char(
        compute="_compute_creditsafe_parent_password"
    )

    @api.depends("parent_id")
    @api.onchange("parent_id", "creditsafe_use_parent_company")
    def _compute_creditsafe_parent_url(self):
        for rec in self:
            if rec.parent_id and rec.creditsafe_use_parent_company:
                rec.creditsafe_parent_url = rec.get_parent_creditsafe_field(
                    "creditsafe_url"
                )
            else:
                rec.creditsafe_parent_url = False

    @api.depends("parent_id")
    @api.onchange("parent_id", "creditsafe_use_parent_company")
    def _compute_creditsafe_parent_username(self):
        for rec in self:
            if rec.parent_id and rec.creditsafe_use_parent_company:
                rec.creditsafe_parent_username = (
                    rec.get_parent_creditsafe_field("creditsafe_username")
                )
            else:
                rec.creditsafe_parent_username = False

    @api.depends("parent_id")
    @api.onchange("parent_id", "creditsafe_use_parent_company")
    def _compute_creditsafe_parent_password(self):
        for rec in self:
            if rec.parent_id and rec.creditsafe_use_parent_company:
                rec.creditsafe_parent_password = (
                    rec.get_parent_creditsafe_field("creditsafe_password")
                )
            else:
                rec.creditsafe_parent_password = False

    @api.depends("coreff_connector_id")
    @api.onchange("coreff_connector_id")
    def _compute_creditsafe_visibility(self):
        for rec in self:
            if rec.coreff_connector_id == self.env.ref(
                "coreff_creditsafe.coreff_connector_creditsafe_api"
            ):
                rec.creditsafe_visibility = True
            else:
                rec.creditsafe_visibility = False

    def get_parent_creditsafe_field(self, field):
        for rec in self:
            if not rec.creditsafe_use_parent_company:
                return rec[field]
            elif rec.parent_id:
                return rec.parent_id.get_parent_creditsafe_field(field)
            else:
                return None
