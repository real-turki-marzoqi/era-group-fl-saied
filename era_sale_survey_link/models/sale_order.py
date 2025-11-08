# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_related_survey(self):
        self.ensure_one()
        if not self.quotation_category_id:
            raise UserError(_("No quotation category set on this order."))

        survey = self.env["survey.survey"].search([
            ("survey_category_id", "=", self.quotation_category_id.id)
        ], limit=1)

        if not survey:
            raise UserError(_("No survey found for the selected category."))

        survey_sudo = survey.sudo()
        user = self.env.user

        existing_answer = self.env["era.survey.answer"].sudo().search([
            ("survey_id", "=", survey.id),
            ("partner_id", "=", self.partner_id.id),
            ("sale_order_id", "=", self.id)
        ], limit=1)

        answer_sudo = existing_answer or self.env["era.survey.answer"].sudo().create({
            'partner_id': self.partner_id.id,
            'email': self.partner_id.email,
            'survey_id': survey_sudo.id,
            'sale_order_id': self.id
        })
        if not existing_answer:
            self._create_empty_lines(survey_sudo, answer_sudo)

        if answer_sudo.state != 'done':
            action = self.env["ir.actions.actions"]._for_xml_id("era_sale_survey_link.action_era_survey_answer")
            action.update({
                'views': [(False, 'form')],
                'view_mode': 'form',
                'res_id': answer_sudo.id,
                'domain': [('id', '=', answer_sudo.id)],
            })
            return action
        elif answer_sudo.state == 'done':
            form_view = self.env.ref("survey.survey_user_input_view_form")

            return {
                "type": "ir.actions.act_window",
                "name": _("Survey Response"),
                "res_model": "survey.user_input",
                "res_id": answer_sudo.survey_input_id.id,
                "view_mode": "form",
                "view_id": form_view.id,
                "target": "current",
            }







    def _create_empty_lines(self, survey, answer_sudo):
        """Create empty survey.user_input.line for all questions in the survey with correct answer_type."""
        Question = self.env["survey.question"].sudo()
        AnswerLine = self.env["era.survey.answer.line"].sudo()

        TYPE_MAP = {
            "simple_choice": "suggestion",
            "multiple_choice": "suggestion",
            "text_box": "text_box",
            "char_box": "char_box",
            "numerical_box": "numerical_box",
            "scale": "scale",
            "date": "date",
            "datetime": "datetime",
            "matrix": "suggestion",  # matrix uses suggestion type too
        }

        all_questions = Question.search([("survey_id", "=", survey.id)])

        for question in all_questions:
            if question.question_type:
                base_vals = {
                    "survey_id": survey.id,
                    "era_answer_id": answer_sudo.id,
                    "question_id": question.id,
                    "answer_type": TYPE_MAP.get(question.question_type, False),
                    'display_name': ''
                }

                if question.question_type == "matrix":
                    for row in question.matrix_row_ids:
                        vals = dict(base_vals, matrix_row_id=row.id)
                        AnswerLine.create(vals)
                else:
                    AnswerLine.create(base_vals)
