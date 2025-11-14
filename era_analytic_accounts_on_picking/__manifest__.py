# -*- coding: utf-8 -*-

{
    "name": "Era Analytic Account on Stock Picking",
    "version": "18.0.1.0.0",
    "author": "Era Group",
    "maintainter": "Said Kraim",
    "summary": """Analytic Account and Analytic Tags Features for Stock Picking""",
    "description": """
        =======================================
        Era Analytic Account on Stock Picking
        =======================================
            
        Analytic Account and Analytic Tags Features for Stock Picking
    
    """,

    "depends": ["stock_account", "analytic"],

    "data": [
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
