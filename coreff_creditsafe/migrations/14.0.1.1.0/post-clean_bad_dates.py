from openupgradelib import openupgrade
from datetime import datetime


@openupgrade.migrate()
def migrate(env, version):
    for partner_id in (
        env["res.partner"].with_context(active_test=False).search([])
    ):
        if (
            isinstance(partner_id.creditsafe_incorporation_date, datetime)
            and partner_id.creditsafe_incorporation_date.year < 1000
        ):
            partner_id.creditsafe_incorporation_date = False

        if (
            isinstance(partner_id.creditsafe_last_judgement_date, datetime)
            and partner_id.creditsafe_last_judgement_date.year < 1000
        ):
            partner_id.creditsafe_last_judgement_date = False

        if (
            isinstance(partner_id.creditsafe_yearenddate, datetime)
            and partner_id.creditsafe_yearenddate.year < 1000
        ):
            partner_id.creditsafe_yearenddate = False
