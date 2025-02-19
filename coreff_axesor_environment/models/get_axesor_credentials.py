from odoo import api, fields, models


class GetAxesorCredentials(models.Model):
    """This class is used to get the credentials from the config file"""

    _name = "get.axesor.credentials"
    _inherit = ["get.axesor.credentials", "server.env.mixin"]

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        cred_fields = {"user": {}, "password": {}}
        cred_fields.update(base_fields)
        return cred_fields
