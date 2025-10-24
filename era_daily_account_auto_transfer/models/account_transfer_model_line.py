from odoo import fields, models, api, _
from odoo.tools import frozendict, format_date, float_compare, format_list, Query


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    account_transfer_id = fields.Many2one('account.transfer.model.line')


class TransferModelLine(models.Model):
    _name = "account.transfer.model.line"
    _inherit = ["account.transfer.model.line", "analytic.mixin"]

    parent_state = fields.Selection(related='transfer_model_id.state', store=True)

    # === Analytic fields === #
    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line', inverse_name='account_transfer_id',
        string='Analytic lines',
    )

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
    )

    def _inverse_analytic_distribution(self):
        """ Unlink and recreate analytic_lines when modifying the distribution."""
        if self.env.context.get('skip_analytic_sync'):
            return
        lines_to_modify = self.env['account.transfer.model.line'].browse([
            line.id for line in self if line.parent_state == "in_progress"
        ]).with_context(skip_analytic_sync=True)
        lines_to_modify.analytic_line_ids.unlink()
        lines_to_modify._create_analytic_lines()

    def _prepare_analytic_lines(self):
        self.ensure_one()
        analytic_line_vals = []
        if self.analytic_distribution:
            # distribution_on_each_plan corresponds to the proportion that is distributed to each plan to be able to
            # give the real amount when we achieve a 100% distribution
            distribution_on_each_plan = {}
            for account_ids, distribution in self.analytic_distribution.items():
                line_values = self._prepare_analytic_distribution_line(float(distribution), account_ids, distribution_on_each_plan)
                if not self.env.company.currency_id.is_zero(line_values.get('amount')):
                    analytic_line_vals.append(line_values)
        return analytic_line_vals

    def _prepare_analytic_distribution_line(self, distribution, account_ids, distribution_on_each_plan):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            analytic tags with analytic distribution.
        """
        self.ensure_one()
        account_field_values = {}
        decimal_precision = self.env['decimal.precision'].precision_get('Percentage Analytic')
        amount = 0
        for account in self.env['account.analytic.account'].browse(map(int, account_ids.split(","))).exists():
            distribution_plan = distribution_on_each_plan.get(account.root_plan_id, 0) + distribution
            if float_compare(distribution_plan, 100, precision_digits=decimal_precision) == 0:
                amount = -self.amount * (100 - distribution_on_each_plan.get(account.root_plan_id, 0)) / 100.0
            else:
                amount = -self.amount * distribution / 100.0
            distribution_on_each_plan[account.root_plan_id] = distribution_plan
            account_field_values[account.plan_id._column_name()] = account.id
        default_name = self.transfer_model_id.name
        return {
            'name': default_name,
            'date': self.transfer_model_id.date_start,
            **account_field_values,
            'partner_id': self.partner_ids[:1].id,
            'unit_amount': 1,
            # 'product_id': self.product_id and self.product_id.id or False,
            # 'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'general_account_id': self.account_id.id,
            # 'ref': self.ref,
            'account_transfer_id': self.id,
            'user_id': self._uid,
            'company_id': self.env.company.id,
            'category': 'other',
        }

    def _create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic distribution.
        """
        # self._validate_analytic_distribution()
        analytic_line_vals = []
        for line in self:
            analytic_line_vals.extend(line._prepare_analytic_lines())

        context = dict(self.env.context)
        context.pop('default_account_id', None)
        context['skip_analytic_sync'] = True
        self.env['account.analytic.line'].with_context(context).create(analytic_line_vals)


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
