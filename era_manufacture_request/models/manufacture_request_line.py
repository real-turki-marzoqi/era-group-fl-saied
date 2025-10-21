# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class ManufacturingRequestLine(models.Model):
    _name = "manufacturing.request.line"
    _description = "Manufacturing Request Line"

    request_id = fields.Many2one("manufacturing.request", string="Request", ondelete="cascade")
    mrp_production_id = fields.Many2one('mrp.production')

    product_id = fields.Many2one("product.product", string="Product", required=True)
    on_hand_qty = fields.Float('On Hand Quantity')
    order_qty = fields.Float('Order Quantity')
    product_qty = fields.Float(string="Quantity To Produce", compute='_compute_product_qty', store=True)

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @api.depends('on_hand_qty', 'order_qty')
    def _compute_product_qty(self):
        for line in self:
            line.product_qty = line.order_qty - line.on_hand_qty
