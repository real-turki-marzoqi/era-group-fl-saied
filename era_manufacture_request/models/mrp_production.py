# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    branch_id = fields.Many2one("stock.warehouse",
                                string="Branch")
