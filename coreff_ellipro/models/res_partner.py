from odoo import models


class Partner(models.Model):
    """
    Add ellipro fields from ElliproDataMixin
    """

    _name = "res.partner"
    _inherit = ["res.partner", "coreff.ellipro.data.mixin"]
