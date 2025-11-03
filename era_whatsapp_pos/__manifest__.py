# -*- coding: utf-8 -*-

{
    "name": "Era Whatsapp POS",
    "version": "18.0.1.0.0",
    "author": "Era Group",
    "maintainter": "Said Kraim",
    "summary": "Add new botton to re-send recipt on Whatsapp message",
    "description": """
    =======================================
    Era Whatsapp POS
    =======================================
        
        Add new botton to re-send recipt on Whatsapp message   
         
    """,

    "depends": ["whatsapp_pos", "point_of_sale"],

    "data": [

    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'era_whatsapp_pos/static/src/**/*',
        ],
    },

    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
