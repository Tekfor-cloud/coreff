# -*- coding: utf-8 -*-
"""
Created on 13 October 2020

@author: D. Couppe
@copyright: ©2018-2019 Article 714
@license: LGPL v3
"""

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("coreff_company_code", "country_id")
    def coreff_update_siret(self):
        for rec in self:
            if rec.country_id.code == "FR" and rec.coreff_company_code:
                rec.siret = rec.coreff_company_code + "*" * max(
                    14 - len(rec.coreff_company_code), 0
                )
