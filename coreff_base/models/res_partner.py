"""
Created on 8 August 2018

@author: J. Carette
@copyright: ©2018-2019 Article 714
@license: LGPL v3
"""

import logging

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.osv import expression


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
        logging.debug("CREATE FROM CALL")
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

    @api.depends(
        "is_company",
        "name",
        "parent_id.name",
        "type",
        "company_name",
    )
    def _compute_display_name(self):
        diff = dict(
            show_address=None,
            show_address_only=None,
            show_email=None,
            html_format=None,
        )
        names = dict(super(ResPartner, self.with_context(**diff)).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    def name_get(self):
        res = []
        for rec in self:
            name = rec._get_name()
            if rec.coreff_company_code:
                name += f" : {rec.coreff_company_code}"
            res.append((rec.id, name))
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        name_res = super(ResPartner, self)._name_search(
            name, args, operator, limit, name_get_uid
        )
        code_res = self._search(
            [("coreff_company_code", operator, name)],
            limit=limit,
            access_rights_uid=name_get_uid,
        )
        return list(set(name_res + list(code_res)))
