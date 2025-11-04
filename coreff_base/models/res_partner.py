"""
Created on 8 August 2018

@author: J. Carette
@copyright: ©2018-2019 Article 714
@license: LGPL v3
"""

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    _sql_constraints = [
        (
            "coreff_company_code_uniq",
            "unique (coreff_company_code, company_id)",
            "Company code must be unique",
        )
    ]

    _rec_names_search = [
        "complete_name",
        "email",
        "ref",
        "vat",
        "company_registry",
        "coreff_company_code",
    ]

    # CM: Add company_id field manually as required to set default
    # to current company
    company_id = fields.Many2one(
        "res.company", index=True, default=lambda self: self.env.company
    )
    coreff_company_code = fields.Char()
    coreff_company_code_mandatory = fields.Boolean(
        related="company_id.coreff_company_code_mandatory"
    )
    coreff_company_score = fields.Integer(string="Rating in %", readonly=True)
    coreff_credit_limit = fields.Integer(readonly=True)
    coreff_activity_code = fields.Char(string="Activity Code")

    # -------------------------
    # unimplemented method that will be defined in other module to
    # update from HMI, only runs validators by default
    def interactive_update(self):
        # just call data valition methods
        self.run_validators()
        return

    # -------------------------
    # method to validate values from CoreFF Partner model
    def run_validators(self):
        # TODO
        return

    def create_from(self):
        # TODO
        return

    @api.model
    def create(self, values):
        rec = super(ResPartner, self).create(values)
        rec._check_company_code()
        return rec

    def write(self, values):
        if "coreff_activity_code" in values:
            if not self.industry_id:
                code = values["coreff_activity_code"]
                code = f"{code[0:2]}.{code[2:4]}"
                industry_id = self.env["res.partner.industry"].search(
                    [("full_name", "like", code)], limit=1
                )
                values["industry_id"] = industry_id.id

        res = super(ResPartner, self).write(values)
        if (
            values.get("is_company")
            or values.get("coreff_company_code_mandatory")
            or "coreff_company_code" in values
        ):
            self._check_company_code()
        return res

    def _check_company_code(self):
        for rec in self:
            if (
                rec.is_company
                and rec.coreff_company_code_mandatory
                and not rec.coreff_company_code
            ):
                raise UserError(_("Company code is required"))

    @api.depends("coreff_company_code")
    def _compute_display_name(self):
        super()._compute_display_name()
        for partner in self.filtered("coreff_company_code"):
            partner.display_name += f" : {partner.coreff_company_code}"

    # Based on https://github.com/OCA/l10n-spain/blob/16.0/l10n_es_partner/models/res_partner.py
    @api.model
    def _get_coreff_company_code_pattern(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("coreff_base.name_pattern", default="")
        )
