from odoo import fields, models, api, _


class TransferModelLine(models.Model):
    _inherit = "account.transfer.model.line"

    amount = fields.Float(
        string="Fixed Amount",
        help="Fixed amount to transfer instead of percentage.",
    )

    @api.depends('analytic_account_ids', 'partner_ids')
    def _compute_percent_is_readonly(self):
        """Hide percent if using fixed amount logic"""
        for record in self:
            record.percent_is_readonly = True  # always readonly

    # Override for fixed amount computation
    def _get_transfer_values(self, account, amount, is_debit, write_date):
        """
        Override to use fixed amount instead of percent if defined.
        """
        self.ensure_one()

        # If amount field is defined, use it directly
        if self.amount:
            transfer_amount = self.amount
        else:
            transfer_amount = amount * (self.percent / 100.0)

        # Create the two lines (destination + origin)
        return [
            self._get_destination_account_transfer_move_line_values(account, transfer_amount, is_debit, write_date),
            self._get_origin_account_transfer_move_line_values(account, transfer_amount, is_debit, write_date),
        ]
