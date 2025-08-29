# ©2018-2019 Article714
# # License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api
from odoo.tools.safe_eval import safe_eval


class CoreffAPI(models.Model):
    """
    Coreff API
    """

    _name = "coreff.api"
    _description = "Coreff API"

    @api.model
    def get_companies(self, arguments):
        """
        Get companies
        """
        company = self.env.user.company_id
        connector = company.coreff_connector_id
        if connector:
            return safe_eval(
                connector.get_companies_def,
                {"self": connector, "arguments": arguments},
            )
        return False

    @api.model
    def get_company(self, arguments):
        """
        Get company information
        """
        company = self.env.user.company_id
        connector = company.coreff_connector_id
        if connector:
            return safe_eval(
                connector.get_company_def,
                {"self": connector, "arguments": arguments},
            )
        return False
