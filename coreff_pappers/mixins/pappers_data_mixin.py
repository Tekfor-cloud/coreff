from odoo import fields, models
from .. import pappers as PA
from odoo.exceptions import UserError


class PappersDataMixin(models.AbstractModel):
    """
    Fields for pappers informations
    """

    _name = "coreff.pappers.data.mixin"
    _description = "Coreff Pappers Data Mixin"

    pappers_visibility = fields.Boolean(compute="_compute_pappers_visibility")

    pappers_identifiant_interne = fields.Char()
    pappers_note = fields.Char()
    pappers_json = fields.Text()

    def _compute_pappers_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            rec.pappers_visibility = company.coreff_connector_id == self.env.ref(
                "coreff_pappers.coreff_connector_pappers_api"
            )

    def pappers_retrieve_directors(self):
        """Create new partners linked to the company."""
        for rec in self:
            if len(rec.coreff_company_code) != 14:
                raise UserError(
                    "Merci de remplacer le n° de SIREN par un n° de SIRET.\n Vous pouvez simplement ajouter un 0 à la fin du n° de SIREN afin d'obtenir les différents n° de SIRET"
                )
            directors = PA.search_directors(
                self.env.user.company_id.pappers_api_token,
                rec.coreff_company_code,
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

    def pappers_get_infos(self):
        for rec in self:
            infos = PA.search_infos(
                self.env.user.company_id.pappers_api_token,
                rec.coreff_company_code,
            )
            self.pappers_json = infos["json"]

    def pappers_get_report(self):
        for rec in self:
            if len(rec.coreff_company_code) == 14:
                code_type = "siret"
            elif 9 <= len(rec.coreff_company_code) < 14:
                code_type = "siren"
            else:
                raise UserError("Numéro de SIREN / SIRET invalide.")
            b64_pdf = PA.search_report(
                self.env.user.company_id.pappers_api_token,
                rec.coreff_company_code,
                code_type,
            )
            name = rec.name + " Report.pdf"
            return self.env["ir.attachment"].create(
                {
                    "name": name,
                    "type": "binary",
                    "datas": b64_pdf,
                    "store_fname": name,
                    "res_model": self._name,
                    "res_id": self.id,
                    "mimetype": "application/x-pdf",
                }
            )
