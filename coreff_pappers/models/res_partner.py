from odoo import models


class Partner(models.Model):
    """
    Add pappers fields from PappersDataMixin
    """

    _name = "res.partner"
    _inherit = ["res.partner", "coreff.pappers.data.mixin"]
