# coding: utf-8
# @author: J. Carette
# @author: C. Guychard (Article714, Tekfor)
# @author: Chris Mann (Open User Systems)
# @copyright: ©2018-2019 Article 714
# @license: LGPL v3

{
    "name": "CoreFF: Basic Module",
    "version": "13.0.2.0.0",
    "category": "CoreFF",
    "author": "Article714",
    "license": "LGPL-3",
    "website": "https://www.article714.org",
    "summary": "Manage Core Financial Data: base module",
    "depends": ["base", "web"],
    "data": [
        "security/coreff_security.xml",
        "views/coreff_autocomplete_assets.xml",
        "views/coreff_config_views.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
    ],
    "qweb": ["static/src/xml/coreff_autocomplete.xml"],
    "installable": True,
    "images": [],
    "application": False,
}
