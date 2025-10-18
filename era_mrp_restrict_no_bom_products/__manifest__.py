# -*- coding: utf-8 -*-

{
    "name": "Era MRP Restrict No BOM Products",
    "version": "18.0.1.0.0",
    'category': 'Inventory/Stock',
    "author": "Era Group",
    "maintainter": "Said Kraim",

    "summary": "Restrict Manufacturing Orders to products with a Bill of Materials",

    "description": """
    =======================================
    Era MRP Restrict No BOM Products
    =======================================

    This module enhances the manufacturing workflow by ensuring that users can only
    create Manufacturing Orders for products that have a defined Bill of Materials (BoM).

    """,

    "depends": ["mrp"],

    "data": [
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
