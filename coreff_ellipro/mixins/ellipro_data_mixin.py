from odoo import fields, models
from .. import ellipro as EP


class ElliproDataMixin(models.AbstractModel):
    """
    Fields for ellipro informations
    """

    _name = "coreff.ellipro.data.mixin"
    _description = "Coreff Ellipro Data Mixin"

    ellipro_visibility = fields.Boolean(compute="_compute_ellipro_visibility")

    ellipro_identifiant_interne = fields.Char()
    ellipro_siret = fields.Char()
    ellipro_siren = fields.Char()
    ellipro_name = fields.Char()
    ellipro_business_name = fields.Char()
    ellipro_trade_name = fields.Char()
    ellipro_city = fields.Char()
    ellipro_zipcode = fields.Char()
    ellipro_street_address = fields.Char()
    ellipro_phone_number = fields.Char()

    ellipro_order_result = fields.Char()
    ellipro_rating_score = fields.Integer()
    ellipro_rating_riskclass = fields.Integer()
    ellipro_order_product = fields.Char(default="50001")  #! temp

    def _compute_ellipro_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            rec.ellipro_visibility = (
                company.coreff_connector_id
                == self.env.ref("coreff_ellipro.coreff_connector_ellipro_api")
            )

    def ellipro_order(self):
        request_type = EP.RequestType.ONLINEORDER.value
        order_request = EP.Order(
            self.ellipro_identifiant_interne, self.ellipro_order_product
        )

        admin = EP.Admin(
            self.env.user.company_id.ellipro_contract,
            self.env.user.company_id.ellipro_user,
            self.env.user.company_id.ellipro_password,
        )

        result = EP.search(admin, order_request, request_type)
        parsed_result = EP.parse_order(result)
        self.ellipro_order_result = parsed_result["ellipro_order_result"]
        self.ellipro_rating_score = parsed_result["ellipro_rating_score"]
        self.ellipro_rating_riskclass = parsed_result[
            "ellipro_rating_riskclass"
        ]
