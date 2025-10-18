# -*- coding: utf-8 -*-

{
    "name": "Era Type Invoice",
    "version": "18.0.1.0.0",
    "author": "Era Group",
    "maintainter": "Said Kraim",
    "summary": "Add new fields type invoice (factory/ Residence/ Transport/ Head Office)",
    "description": """
    =======================================
    Era Type Invoice
    =======================================
        
    Add new fields type invoice (factory/ Residence/ Transport/ Head Office) on Invoice (account.move)
    
    """,

    "depends": ["account"],

    "data": [
        "views/account_move.xml"
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
