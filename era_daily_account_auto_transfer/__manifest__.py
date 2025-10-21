# -*- coding: utf-8 -*-

{
    "name": "Era Daily Account Auto Transfer",
    "version": "18.0.1.0.0",
    "category": "Accounting/Accounting",
    "author": "Era Group",
    "maintainter": "Said Kraim",

    "summary": "Account Automated Transfers Daily with Fixed Amount",

    "description": """
    =======================================
    Era Daily Account Auto Transfer
    =======================================

    Account Automated Transfers Daily with Fixed Amount

    """,

    "depends": ["account", 'account_auto_transfer'],

    "data": [
        "data/ir_cron.xml",
        "views/account_transfer_model.xml"
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
