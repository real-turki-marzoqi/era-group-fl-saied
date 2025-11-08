# -*- coding: utf-8 -*-
{
    "name": "Era Sale ↔ Survey Link",
    "version": "18.0.1.0.0",
    "summary": "Link Sale Orders with Surveys: category sync, creation, and constraints",
    "author": "Era Group | Developer : Turki Marzoqi",
    "website": "",
    "license": "OPL-1",
    "depends": ["sale_management", "survey", "era_fitness_sale_ext"],
    "data": [
        "security/ir.model.access.csv",

        "views/survey_views.xml",
        "views/sale_order_view.xml",
        "views/survey_user_input_view.xml",
        "views/era_survey_answer_views.xml",
    ],
    "installable": True,
}
