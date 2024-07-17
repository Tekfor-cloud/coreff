from odoo import fields, models
from .. import pappers as PA


class PappersDataMixin(models.AbstractModel):
    """
    Fields for pappers informations
    """

    _name = "coreff.pappers.data.mixin"
    _description = "Coreff Pappers Data Mixin"

    pappers_visibility = fields.Boolean(compute="_compute_pappers_visibility")

    pappers_identifiant_interne = fields.Char()

    def _compute_pappers_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            rec.pappers_visibility = company.coreff_connector_id == self.env.ref(
                "coreff_pappers.coreff_connector_pappers_api"
            )

    def retrieve_directors(self):
        """Create new partners linked to the company."""
        for rec in self:
            directors = PA.search_directors(
                self.env.user.company_id.pappers_api_token, rec.coreff_company_code
            )
            for director in directors:
                self.env["res.partner"].create(
                    {
                        "name": director["name"],
                        "parent_id": self.id,
                        "company_type": "person",
                        "function": director["job"],
                        "street": director["street"],
                        "city": director["city"],
                        "zip": director["zip"],
                        "type": "other",
                    }
                )
