# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    onhand_qty = fields.Float(string="On Hand Qty", compute="_compute_stock_quantities")
    reserved_qty = fields.Float(string="Reserved Qty", compute="_compute_stock_quantities")
    available_qty = fields.Float(string="Free to Use Qty", compute="_compute_stock_quantities")
    saved_location_qty = fields.Float(string="Saved Location Qty", compute="_compute_stock_quantities")

    @api.depends('product_id')
    def _compute_stock_quantities(self):
        StockQuant = self.env['stock.quant'].sudo()
        for line in self:
            onhand = reserved = saved = 0.0
            wh = line.order_id.warehouse_id
            product = line.product_id

            if not product or not wh:
                line.onhand_qty = line.reserved_qty = line.available_qty = line.saved_location_qty = 0
                continue

            # 1- All internal locations of the warehouse
            internal_locations = self.env['stock.location'].search([
                ('usage', '=', 'internal'),
                ('id', 'child_of', wh.view_location_id.id)
            ])
            if internal_locations:
                quants = StockQuant.read_group(
                    [('product_id', '=', product.id), ('location_id', 'in', internal_locations.ids)],
                    ['quantity:sum', 'reserved_quantity:sum'], ['product_id']
                )
                if quants:
                    onhand = quants[0]['quantity']
                    reserved = quants[0]['reserved_quantity']

            # 2- Custom Locations of Type “is_saved”
            saved_locations = self.env['stock.location'].search([
                ('is_saved', '=', True),
            ])
            if saved_locations:
                quants_saved = StockQuant.read_group(
                    [('product_id', '=', product.id), ('location_id', 'in', saved_locations.ids)],
                    ['quantity:sum'], ['product_id']
                )
                if quants_saved:
                    saved = quants_saved[0]['quantity']

            line.onhand_qty = onhand
            line.reserved_qty = reserved
            line.available_qty = onhand - reserved
            line.saved_location_qty = saved
