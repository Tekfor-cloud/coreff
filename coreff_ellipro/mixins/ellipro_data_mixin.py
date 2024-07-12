# -*- coding: utf-8 -*-
# ©2018-2019 Article714
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
from odoo import fields, models
from datetime import datetime
import logging
from .. import ellipro as EP
import xml.etree.ElementTree as ET
import requests

logger = logging.getLogger()


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
            rec.ellipro_visibility = company.coreff_connector_id == self.env.ref(
                "coreff_ellipro.coreff_connector_ellipro_api"
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

        headers = {"Content-Type": "application/xml"}

        root = ET.Element(
            f"{request_type}Request", attrib={"lang": "FR", "version": "2.2"}
        )
        admin.set_element(root)
        order_request.set_element(root)
        body = ET.tostring(root)

        request = requests.post(
            f"https://services-test.data-access-gateway.com/1/rest/{request_type}",
            data=body,
            headers=headers,
        )

        logger.info(
            "\n-------------------------------\nellipro_order\n-------------------------------"
        )
        logger.info(request.text)
        result = ET.fromstring(request.text)
        for response in result.findall("response"):
            name = response.findall("intlReport/header/report/reportId")[0].text
            price = (
                response.findall("intlReport/header/report/defaultCurrencyUnit")[0].text
                + " "
                + response.findall("intlReport/header/report/defaultCurrency")[0].text
            )
            self.ellipro_order_result = name + " pour le prix de " + price
            logger.info(
                response.findall(
                    "intlReport/assessmentData/score/value[@type='score']"
                )[0].text
            )
            logger.info(
                response.findall(
                    "intlReport/assessmentData/score/value[@type='riskclass']"
                )[0].text
            )
            self.ellipro_rating_score = (
                int(
                    response.findall(
                        "intlReport/assessmentData/score/value[@type='score']"
                    )[0].text
                )
                * 10
            )  # * rating goes from 0 to 10, rating*10 for % value
            rating_riskclass = response.findall(
                "intlReport/assessmentData/score/value[@type='riskclass']"
            )[0].text
            self.ellipro_rating_riskclass = (
                (4 - (ord(rating_riskclass) - 65)) / 4 * 100
            )  # * letter given goes from A for best to E for worst, converted to 0-4 scale then to %
