from odoo import models


class Partner(models.Model):
    """
    Add pappers fields from AxesorDataMixin
    """

    _name = "res.partner"
    _inherit = ["res.partner", "coreff.axesor.data.mixin"]
