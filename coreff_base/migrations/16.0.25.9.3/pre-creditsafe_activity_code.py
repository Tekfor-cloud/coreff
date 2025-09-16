from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    if openupgrade.column_exists(
        env.cr, "res_partner", "credisafe_activity_code"
    ):
        openupgrade.copy_columns(
            env.cr,
            {
                "res_partner": [
                    ("credisafe_activity_code", "credisafe_activity_code_old")
                ]
            },
        )
