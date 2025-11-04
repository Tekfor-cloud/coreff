from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if env.ref("coreff_base.view_coreff_config", raise_if_not_found=False):
        env.ref("coreff_base.view_coreff_config").unlink()
