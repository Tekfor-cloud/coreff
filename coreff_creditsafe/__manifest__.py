# @author: J. Carette
# @author: C. Guychard
# @author: Chris Mann (Open User Systems)
# @copyright: ©2018-2019 Article 714
# @license: LGPL v3

{
    "name": "CoreFF: CreditSafe",
    "version": "16.0.1.1.0",
    "category": "CoreFF",
    "author": "Article714",
    "license": "LGPL-3",
    "website": "https://www.article714.org",
    "summary": "",
    "depends": ["coreff_base", "web", "crm"],
    "data": [
        "security/creditsafe_security.xml",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
        "data/coreff_connector.xml",
    ],
    "qweb": [],
    "installable": True,
    "images": [],
    "application": False,
}
