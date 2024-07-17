from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    pappers_visibility = fields.Boolean(compute="_compute_pappers_visibility")

    pappers_api_token = fields.Char()

    @api.depends("coreff_connector_id")
    @api.onchange("coreff_connector_id")
    def _compute_pappers_visibility(self):
        for rec in self:
            rec.pappers_visibility = rec.coreff_connector_id == self.env.ref(
                "coreff_pappers.coreff_connector_pappers_api"
            )
