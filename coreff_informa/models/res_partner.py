# -*- coding: utf-8 -*-
# ©2018-2019 Article714
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class Partner(models.Model):
    """
    Add informa fields from InformaDataMixin
    """

    _name = "res.partner"
    _inherit = ["res.partner", "coreff.informa.data.mixin"]
