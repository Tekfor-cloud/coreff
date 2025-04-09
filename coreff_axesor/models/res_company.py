from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    axesor_api_token = fields.Char()
