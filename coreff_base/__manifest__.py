# @author: J. Carette
# @author: C. Guychard (Article714, Tekfor)
# @author: Chris Mann (Open User Systems)
# @copyright: ©2018-2019 Article 714
# @license: LGPL v3

{
    "name": "CoreFF: Basic Module",
    "version": "16.0.1.1.0",
    "category": "CoreFF",
    "author": "Article714",
    "license": "LGPL-3",
    "website": "https://www.article714.org",
    "summary": "Manage Core Financial Data: base module",
    "depends": ["base", "web"],
    "data": [
        "security/coreff_security.xml",
        "views/coreff_config_views.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "coreff_base/static/src/scss/coreff_autocomplete.scss",
            "coreff_base/static/src/js/create_from_button.js",
            "coreff_base/static/src/js/coreff_autocomplete_core.js",
            "coreff_base/static/src/js/coreff_autocomplete_fieldchar.js",
        ],
        "web.assets_qweb": [
            "coreff_base/static/src/xml/coreff_autocomplete.xml",
        ],
    },
    "installable": True,
    "images": [],
    "application": False,
}
