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

    ellipro_order_result = fields.Char()
    ellipro_rating_score = fields.Integer()
    ellipro_rating_riskclass = fields.Integer()

    ellipro_data = fields.Text()
    ellipro_order_data = fields.Text()

    def _compute_ellipro_visibility(self):
        company = self.env.user.company_id
        for rec in self:
            rec.ellipro_visibility = company.coreff_connector_id == self.env.ref(
                "coreff_ellipro.coreff_connector_ellipro_api"
            )

    def ellipro_get_infos(self):
        for rec in self:
            if self.country_id["id"]:
                country = (
                    self.env["res.country"]
                    .browse(int(self.country_id["id"]))
                    .code_alpha3
                )
            else:
                country = "FRA"

            search_type = EP.SearchType.ID
            request_type = EP.RequestType.SEARCH.value
            if country == "FRA":
                type_attribute = EP.IdType.ESTB
            else:
                type_attribute = EP.IdType.REGISTER

            admin = EP.Admin(
                self.env.user.company_id.ellipro_contract,
                self.env.user.company_id.ellipro_user,
                self.env.user.company_id.ellipro_password,
            )
            main_only = "true"
            search_request = EP.Search(
                search_type,
                rec.coreff_company_code,
                self.env.user.company_id.ellipro_max_hits,
                type_attribute,
                main_only,
                country,
            )
            response = EP.search(admin, search_request, request_type)
            response = EP.search_response_handle(response, country)
            if len(response) > 0:
                response = response[0]
            else:
                raise Exception("API Response couldn't be treated")

            self.ellipro_identifiant_interne = response.get(
                "ellipro_identifiant_interne", False
            )
            self.city = response.get("city", False)
            self.zip = response.get("zip", False)
            self.street = response.get("street", False)
            self.phone = response.get("phone", False)
            self.ellipro_data = response.get("ellipro_data", False)

    def ellipro_order(self, file_format):
        request_type = EP.RequestType.ONLINEORDER.value
        order_request = EP.Order(
            self.ellipro_identifiant_interne,
            self.env.user.company_id.ellipro_order_product,
            file_format,
            EP.OutputMethod[file_format],
        )

        admin = EP.Admin(
            self.env.user.company_id.ellipro_contract,
            self.env.user.company_id.ellipro_user,
            self.env.user.company_id.ellipro_password,
        )

        return EP.search(admin, order_request, request_type)

    def ellipro_xml_order(self):
        result = self.ellipro_order("XML")
        parsed_result = EP.parse_order(result)
        self.ellipro_order_result = parsed_result["ellipro_order_result"]
        self.ellipro_rating_score = parsed_result["ellipro_rating_score"]
        self.ellipro_rating_riskclass = parsed_result["ellipro_rating_riskclass"]
        self.ellipro_order_data = parsed_result["ellipro_order_data"]

    def ellipro_pdf_order(self):
        result = self.ellipro_order("PDF")
        for rec in self:
            name = rec.name + " Ellipro Report.pdf"
            return self.env["ir.attachment"].create(
                {
                    "name": name,
                    "type": "binary",
                    "datas": result,
                    "store_fname": name,
                    "res_model": self._name,
                    "res_id": self.id,
                    "mimetype": "application/x-pdf",
                }
            )
