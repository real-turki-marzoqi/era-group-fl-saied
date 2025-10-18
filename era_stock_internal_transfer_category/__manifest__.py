# -*- coding: utf-8 -*-

{
    "name": "Era Internal Transfer Product Category",
    "version": "18.0.1.0.0",
    'category': 'Inventory/Stock',
    "author": "Era Group",
    "maintainter": "Said Kraim",

    "summary": "Limit product selection in internal transfers by category",

    "description": """
    =======================================
    Era Type Invoice
    =======================================

    This module adds a product category restriction feature to internal transfers.
    Users can select an allowed product category, and only products from that
    category can be chosen in the transfer lines.

    """,

    "depends": ["account"],

    "data": [
        "views/stock_picking.xml"
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
