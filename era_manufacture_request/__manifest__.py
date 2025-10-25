# -*- coding: utf-8 -*-

{
    "name": "Era Manufacture Requests",
    "version": "18.0.1.0.0",
    "author": "Era Group",
    "maintainter": "Said Kraim",
    "summary": "Manufacturing requests",
    "description": """
        =======================================
        Era Manufacture Requests
        =======================================
            
        Create manufacturing requests
    
    """,

    "depends": ["mrp", "stock"],

    "data": [
        "security/ir.model.access.csv",
        "views/manufacture_request_views.xml",
        "views/product_product.xml",
        "views/mrp_production.xml",
        "views/res_config_settings_views.xml"
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
