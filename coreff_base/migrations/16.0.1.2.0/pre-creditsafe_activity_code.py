from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    if openupgrade.column_exists(
        env.cr, "res_partner", "creditsafe_activity_code"
    ):
        openupgrade.copy_columns(
            env.cr,
            {
                "res_partner": [
                    (
                        "creditsafe_activity_code",
                        "creditsafe_activity_code_old",
                        None,
                    )
                ]
            },
        )
