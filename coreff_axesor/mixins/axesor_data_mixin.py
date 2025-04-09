from odoo import fields, models, _
from .. import axesor as AX


class AxesorDataMixin(models.AbstractModel):
    """
    Fields for axesor informations
    """

    _name = "coreff.axesor.data.mixin"
    _description = "Coreff Axesor Data Mixin"

    axesor_visibility = fields.Boolean(compute="_compute_axesor_visibility")

    axesor_internal_id = fields.Char()
    axesor_data = fields.Text()

    def _compute_axesor_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            rec.axesor_visibility = (
                company.coreff_connector_id
                == self.env.ref("coreff_axesor.coreff_connector_axesor_api")
            )

    def axesor_retrieve_directors(self):
        """Create new partners linked to the company."""
        for rec in self:
            if len(rec.coreff_company_code) != 14:
                raise Exception(
                    _(
                        "Please replace the SIREN code for a SIRET one. To proceed, you can just add a 0 at the end of the SIREN number to get all different SIRET numbers."
                    )
                )
            directors = AX.get_directors(
                self.env.user.company_id.axesor_api_token,
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

    def axesor_get_infos(self):
        for rec in self:
            infos = AX.get_infos(
                self.env.user.company_id.axesor_api_token,
                rec.coreff_company_code,
            )
            self.axesor_data = infos

    def axesor_get_report(self):
        for rec in self:
            if len(rec.coreff_company_code) == 14:
                code_type = "siret"
            elif 9 <= len(rec.coreff_company_code) < 14:
                code_type = "siren"
            else:
                raise Exception(_("SIREN / SIRET code invalid."))
            b64_pdf = AX.get_report(
                self.env.user.company_id.axesor_api_token,
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
