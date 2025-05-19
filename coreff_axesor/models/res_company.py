from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    axesor_endpoint = fields.Selection(selection=[('sandbox', 'Sandbox'), ('production', 'Production')], default="sandbox")

    axesor_login = fields.Char()
    axesor_password = fields.Char()
