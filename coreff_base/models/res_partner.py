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

    # CM: Add company_id field manually as required to set default
    # to current company
    company_id = fields.Many2one(
        "res.company", index=True, default=lambda self: self.env.company
    )
    coreff_company_code = fields.Char()
    coreff_company_code_mandatory = fields.Boolean(
        related="company_id.coreff_company_code_mandatory"
    )

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
        return super()._compute_display_name()

    def _get_name(self):
        name = super()._get_name()
        if self.is_company:
            name = f"{name} : {self.coreff_company_code}"
        return name

    # Based on https://github.com/OCA/l10n-spain/blob/14.0/l10n_es_partner/models/res_partner.py
    @api.model
    def _get_coreff_company_code_pattern(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("coreff_base.name_pattern", default="")
        )

    # Based on https://github.com/OCA/l10n-spain/blob/14.0/l10n_es_partner/models/res_partner.py
    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Give preference to coreff_company_code on name search, appending
        the rest of the results after. This has to be done this way, as
        Odoo overwrites name_search on res.partner in a non inheritable way."""
        if (
            "%(coreff_company_code_name)s"
            in self._get_coreff_company_code_pattern()
        ):
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )
        if not args:
            args = []
        partner_search_mode = self.env.context.get("res_partner_search_mode")
        order = (
            "{}_rank".format(partner_search_mode)
            if partner_search_mode
            else None
        )
        partners = self.search(
            [("coreff_company_code", operator, name)] + args,
            limit=limit,
            order=order,
        )
        res = models.lazy_name_get(partners)
        if limit:
            limit_rest = limit - len(partners)
        else:  # pragma: no cover
            # limit can be 0 or None representing infinite
            limit_rest = limit
        if limit_rest or not limit:
            args += [("id", "not in", partners.ids)]
            res += super().name_search(
                name, args=args, operator=operator, limit=limit_rest
            )
        return res
