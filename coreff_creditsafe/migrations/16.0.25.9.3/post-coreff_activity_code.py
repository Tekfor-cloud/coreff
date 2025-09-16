from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    if openupgrade.column_exists(
        env.cr, "res_partner", "creditsafe_activity_code_old"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE res_partner partner1
            SET coreff_activity_code = partner2.creditsafe_activity_code_old
            FROM res_partner partner2
            WHERE partner1.id = partner2.id and partner2.creditsafe_activity_code_old IS NOT NULL
            """,
        )

        openupgrade.drop_columns(
            env.cr,
            [
                ("res_partner", "creditsafe_activity_code_old"),
            ],
        )
