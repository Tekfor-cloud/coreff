# ©2018-2019 Article714
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from .. import ellipro as EP
import logging

logger = logging.getLogger()


class ResCompany(models.Model):
    _inherit = "res.company"

    ellipro_visibility = fields.Boolean(compute="_compute_ellipro_visibility")

    # ellipro_user = fields.Char(compute="compute_ellipro_user")
    ellipro_user = fields.Char()
    ellipro_password = fields.Char()
    ellipro_contract = fields.Char()
    ellipro_max_hits = fields.Char()

    @api.depends("coreff_connector_id")
    @api.onchange("coreff_connector_id")
    def _compute_ellipro_visibility(self):
        for rec in self:
            rec.ellipro_visibility = rec.coreff_connector_id == self.env.ref(
                "coreff_ellipro.coreff_connector_ellipro_api"
            )

    @api.onchange("ellipro_user")
    def compute_ellipro_user(self):
        # for record in self:
        # record.ellipro_user = "NN448142"
        logger.info(
            "\n-------------------------------\nDEPEEEEEENDS\n-------------------------------"
        )
        # NN448142


#    @api.depends("ellipro_user")
#    def compute_ellipro_connection(self):
#        admin = EP.Admin(
#            self.ellipro_contract, self.ellipro_user, self.ellipro_password
#        )
#        has_error, error = EP.connection_check(admin)
#        if has_error:
#            print(error)
