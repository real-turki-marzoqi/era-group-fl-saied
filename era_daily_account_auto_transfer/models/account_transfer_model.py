from odoo import fields, models, api, _


class TransferModel(models.Model):
    _inherit = "account.transfer.model"

    frequency = fields.Selection(selection_add=[('day', 'Day')], ondelete={'day': 'cascade'})

    @api.constrains('line_ids')
    def _check_line_ids_percent(self):
        for record in self:
            if all(line.amount for line in record.line_ids):
                continue  # skip percent check when using fixed amounts
            if not (0 < record.total_percent <= 100.0):
                raise ValidationError(
                    _('The total percentage (%s) should be less or equal to 100!', record.total_percent))