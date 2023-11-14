# -*- coding: utf-8 -*-
# ©2018-2019 Article714
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from ..mixins.creditsafe_data_mixin import (
    CreditSafeDataMixin,
)


class Partner(CreditSafeDataMixin, models.Model):
    """
    Add creditsafe fields from CreditSafeDataMixin
    """

    _name = "res.partner"
    _inherit = ["res.partner", "coreff.creditsafe.data.mixin"]

    def retrieve_directors_data(self):
        """
        Retrieve directors contact data for company and store
        """
        for rec in self:
            arguments = {}
            arguments["company_id"] = rec.creditsafe_company_id
            arguments["user_id"] = self.env.user.id
            company = self.env["coreff.api"].get_company(arguments)
            company = company.get("report", {})
            directors = company.get("directors", {}).get(
                "currentDirectors", {}
            )
            # CM: For each director, iterate through retrieving record
            # Next do a check for duplicates and if none present,
            # store the record as a new contact linked to this company.
            for director in directors:
                self.get_director(director)

    def get_director(self, director):
        # CM: Search for any duplicate contacts before taking action
        # - Match name and postcode
        result = self.env["res.partner"].search(
            [
                (
                    "name",
                    "ilike",
                    director.get("firstName", "")
                    + " "
                    + director.get("surname", ""),
                ),
                ("zip", "ilike", director.get("postalCode", "")),
            ]
        )
        if len(result) == 0:
            # CM: Mappings for directors to Odoo res.partner
            # Create partner contact for this director, link to parent company
            position = director.get("positions", {})[0].get("positionName", "")
            address = director.get("address", {})
            # CM: Append housenumber if exists, otherwise use street
            if len(address.get("houseNumber", "")) > 0:
                street = (
                    address.get("houseNumber", "")
                    + " "
                    + address.get("street", "")
                )
            else:
                street = address.get("street", "")
            # CM: If phone exists use it, otherwise use phone from parent
            #  company
            if len(address.get("telephone", "")) > 0:
                telephone = address.get("telephone", "")
            else:
                telephone = self.phone
            self.env["res.partner"].create(
                {
                    "name": director.get("firstName", "")
                    + " "
                    + director.get("surname", ""),
                    "parent_id": self.id,
                    "company_type": "person",
                    "function": position,
                    "ref": director.get("id", ""),
                    "street": street,
                    "city": address.get("city", ""),
                    "zip": address.get("postalCode", ""),
                    "phone": telephone,
                    "type": "other",
                    "title": self.get_title(director.get("title", "")),
                    "state_id": self.get_state(address.get("province", "")),
                    "country_id": self.get_country(address.get("country", "")),
                }
            )
            return True
