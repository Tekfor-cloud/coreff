from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    axesor_visibility = fields.Boolean(
        compute="_compute_axesor_visibility", default=False
    )

    axesor_login = fields.Char()
    axesor_password = fields.Char()

    @api.depends("coreff_connector_id")
    @api.onchange("coreff_connector_id")
    def _compute_axesor_visibility(self):
        for rec in self:
            if rec.coreff_connector_id == self.env.ref(
                "coreff_axesor.coreff_connector_axesor_api"
            ):
                rec.axesor_visibility = True
            else:
                rec.axesor_visibility = False