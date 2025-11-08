from odoo import api, fields, models, _


class ERASurveyAnswer(models.Model):
    _name = 'era.survey.answer'
    _description = 'Survey Answer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'survey_id'

    # ------------------------------------------------------------
    # Champs principaux
    # ------------------------------------------------------------
    survey_id = fields.Many2one(
        'survey.survey', string='Survey', required=True,
        readonly=True, index=True, ondelete='cascade'
    )

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    survey_input_id = fields.Many2one('survey.user_input', string='Survey User Input', readonly=True)

    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')
    ], string='Status', default='new', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Contact', readonly=True, index=True)
    email = fields.Char('Email', readonly=True)

    # Lignes de réponses
    line_ids = fields.One2many(
        'era.survey.answer.line', 'era_answer_id',
        string='Answers', copy=True
    )

    # ------------------------------------------------------------
    # Méthodes internes
    # ------------------------------------------------------------

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_done(self):
        for record in self:
            if not record.line_ids:
                raise UserError(_("You must have at least one answer line before completing the survey."))

            # Filtrer uniquement les lignes sauvegardées
            saved_lines = record.line_ids.filtered(lambda l: l.is_saved)
            if not saved_lines:
                raise UserError(_("You must save at least one answer before marking the survey as done."))

            # Créer le user_input principal
            user_input = self.env['survey.user_input'].create({
                'survey_id': record.survey_id.id,
                'partner_id': record.partner_id.id,
                'email': record.email,
                'state': 'done',
                'test_entry': False,
                'sale_order_id': record.sale_order_id.id,
            })
            self.survey_input_id = user_input.id

            # Créer les lignes associées pour les réponses sauvegardées
            for line in saved_lines:
                vals = {
                    'user_input_id': user_input.id,
                    'question_id': line.question_id.id,
                    'answer_type': line.answer_type,
                }

                # assigner la valeur correcte selon le type
                if line.answer_type == 'char_box':
                    vals['value_char_box'] = line.value_char_box
                elif line.answer_type == 'text_box':
                    vals['value_text_box'] = line.value_text_box
                elif line.answer_type == 'numerical_box':
                    vals['value_numerical_box'] = line.value_numerical_box
                elif line.answer_type == 'scale':
                    vals['value_scale'] = line.value_scale
                elif line.answer_type == 'date':
                    vals['value_date'] = line.value_date
                elif line.answer_type == 'datetime':
                    vals['value_datetime'] = line.value_datetime
                elif line.answer_type == 'suggestion':
                    vals['suggested_answer_id'] = line.suggested_answer_id.id
                    vals['matrix_row_id'] = line.matrix_row_id.id

                self.env['survey.user_input.line'].create(vals)

            # Mettre à jour l’état du survey
            record.state = 'done'
