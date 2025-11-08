# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    survey_category_id = fields.Many2one(
        "product.category",
        string="Survey Category",
        domain=[("appear_in_crm", "=", True)],
        help="Choose a category that is flagged to appear in CRM.",
    )

    # قيد فريد على مستوى قاعدة البيانات (يسمح بتكرار NULL تلقائياً)
    _sql_constraints = [
        ("uniq_survey_per_category",
         "unique(survey_category_id)",
         "Each product category can only have one survey.")
    ]

    @api.constrains("survey_category_id")
    def _check_unique_category(self):
        """رسالة خطأ أوضح قبل ما يطيح في قيد SQL."""
        for rec in self:
            if not rec.survey_category_id:
                continue
            dup = self.search_count([
                ("id", "!=", rec.id),
                ("survey_category_id", "=", rec.survey_category_id.id),
            ])
            if dup:
                raise ValidationError(
                    _("There is already a survey for the selected category: %s")
                    % rec.survey_category_id.display_name
                )
