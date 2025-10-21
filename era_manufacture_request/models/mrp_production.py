# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    # @api.depends('procurement_group_id', 'procurement_group_id.stock_move_ids.group_id')
    # def _compute_picking_ids(self):
    #     super()._compute_picking_ids()
    #     for order in self:
    #         order.picking_ids = order.move_raw_ids.move_orig_ids.picking_id
    #
    #         order.delivery_count = len(order.picking_ids)
