# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_type = fields.Selection([('factory', 'Factory'),
                                 ('residence', 'Residence'),
                                 ('transport', 'Transport'),
                                 ('head_office', 'Head Office'),
                                 ])