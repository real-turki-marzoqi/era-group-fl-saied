from odoo import api, fields, models, _
import textwrap


class ERASurveyAnswerLine(models.Model):
    _name = 'era.survey.answer.line'
    _description = 'Survey Answer Line'
    _order = 'question_sequence, id'

    # ------------------------------------------------------------
    # Liens et métadonnées
    # ------------------------------------------------------------
    era_answer_id = fields.Many2one('era.survey.answer', string='Answer', ondelete='cascade', index=True)
    survey_id = fields.Many2one('era.survey.answer', string='Survey', ondelete='cascade', index=True)
    question_id = fields.Many2one('survey.question', string='Question', required=True, ondelete='cascade', index=True)
    question_sequence = fields.Integer('Sequence', related='question_id.sequence', store=True)

    # ------------------------------------------------------------
    # Type de réponse
    # ------------------------------------------------------------
    answer_type = fields.Selection([
        ('text_box', 'Free Text'),
        ('char_box', 'Text'),
        ('numerical_box', 'Number'),
        ('scale', 'Number'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('suggestion', 'Suggestion'),
    ], string='Answer Type')

    # ------------------------------------------------------------
    # Valeurs de réponse selon le type
    # ------------------------------------------------------------
    value_char_box = fields.Char('Text answer')
    value_numerical_box = fields.Float('Numerical answer')
    value_scale = fields.Integer('Scale value')
    value_date = fields.Date('Date answer')
    value_datetime = fields.Datetime('Datetime answer')
    value_text_box = fields.Text('Free Text answer')

    # Pour les choix suggérés (questions à choix ou matrices)
    suggested_answer_id = fields.Many2one('survey.question.answer', string="Suggested answer")
    matrix_row_id = fields.Many2one('survey.question.answer', string="Row answer")

    is_saved = fields.Boolean(
        string='Answer Saved',
        compute='_compute_is_saved',
        store=True
    )

    @api.depends(
        'answer_type', 'value_text_box', 'value_numerical_box',
        'value_char_box', 'value_date', 'value_datetime',
        'suggested_answer_id.value', 'matrix_row_id.value',
    )
    def _compute_is_saved(self):
        for line in self:
            saved = False
            if line.answer_type == 'char_box' and line.value_char_box:
                saved = True
            elif line.answer_type == 'text_box' and line.value_text_box:
                saved = True
            elif line.answer_type == 'numerical_box' and line.value_numerical_box:
                saved = True
            elif line.answer_type == 'date' and line.value_date:
                saved = True
            elif line.answer_type == 'datetime' and line.value_datetime:
                saved = True
            elif line.answer_type == 'scale' and line.value_scale:
                saved = True
            elif line.answer_type == 'suggestion':
                # suggestion enregistrée si une valeur suggérée est choisie
                if line.suggested_answer_id and line.matrix_row_id:
                    saved = True
                elif line.suggested_answer_id and not line.matrix_row_id:
                    saved = True

            line.is_saved = saved

    # ------------------------------------------------------------
    # Méthodes utilitaires
    # ------------------------------------------------------------
    #
    @api.depends(
        'answer_type', 'value_text_box', 'value_numerical_box',
        'value_char_box', 'value_date', 'value_datetime',
        'suggested_answer_id.value', 'matrix_row_id.value',
    )
    def _compute_display_name(self):
        for line in self:
            if line.answer_type == 'char_box':
                line.display_name = line.value_char_box
            elif line.answer_type == 'text_box' and line.value_text_box:
                line.display_name = textwrap.shorten(line.value_text_box, width=50, placeholder=" [...]")
            elif line.answer_type == 'numerical_box':
                line.display_name = line.value_numerical_box
            elif line.answer_type == 'date':
                line.display_name = fields.Date.to_string(line.value_date)
            elif line.answer_type == 'datetime':
                line.display_name = fields.Datetime.to_string(line.value_datetime)
            elif line.answer_type == 'scale':
                line.display_name = line.value_scale
            elif line.answer_type == 'suggestion':
                if line.suggested_answer_id.value and line.matrix_row_id.value:
                    line.display_name = f'{line.suggested_answer_id.value}: {line.matrix_row_id.value}'
                else:
                    line.display_name = line.suggested_answer_id.value
            if not line.display_name:
                line.display_name = _('Skipped')
