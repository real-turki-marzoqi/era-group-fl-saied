# -*- coding: utf-8 -*-

{
    "name": "ERA Sale Stock Tracking",
    "version": "18.0.1.0.0",
    "author": "Era Group",
    "maintainter": "Said Kraim",
    "summary": "Display real-time on-hand, reserved, available, and saved stock "
               "quantities directly in sale order lines.",
    "description": """
    =======================================
    ERA Sale Stock Tracking
    =======================================
        
        This module enhances the Odoo Sales by providing real-time visibility of stock availability at the 
        sale order line level.
        For each product in a sale order, users can instantly view its current stock situation across 
        warehouse locations — including total on-hand quantity, reserved quantity, available stock, 
        and quantities stored in “saved” (أمانات) locations.
    
    """,

    "depends": ["sale", "stock"],

    "data": [
        "views/sale_order_views.xml",
        "views/stock_location.xml"
    ],

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
