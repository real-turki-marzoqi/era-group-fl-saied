# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class ManufacturingRequest(models.Model):
    _name = "manufacturing.request"
    _description = "manufacturing Request"

    name = fields.Char(string="Reference", default=lambda self: "New", copy=False)
    date = fields.Date(string="Request Date", default=fields.Date.today)
    user_id = fields.Many2one(
        'res.users',
        string='Requested by',
        default=lambda self: self.env.user,
    )
    branch_id = fields.Many2one("stock.warehouse", string="Branch", required=True)
  
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("done", "Done"),
        ("cancel", "Cancel")
    ], default="draft", string="Status")

    line_ids = fields.One2many("manufacturing.request.line", "request_id",
                               string="Request Lines")

    is_set_qty = fields.Boolean()

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company.id)

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})
        self.line_ids.mapped('mrp_production_id').write({'state': 'cancel'})

    def action_set_qty(self):
        qty_type = self.env.context.get('qty_type')
        if not qty_type:
            return

        field_map = {
            'normal': 'days_normal',
            'middle': 'days_middle',
            'weekday': 'days_weekday',
        }

        company_field = field_map.get(qty_type)
        if not company_field:
            return

        qty_value = getattr(self.env.company, company_field, 0)

        for line in self.line_ids:
            line.order_qty = qty_value

        self.is_set_qty = True

    def action_upload_product(self):
        self.ensure_one()
        finished_goods = self.env['product.product'].search([('is_finished_good', '=', True)])
        line_vals = []
        warehouse = self.branch_id
        location = warehouse.lot_stock_id
        StockQuant = self.env['stock.quant']

        for product in finished_goods:
            # Compute available quantity
            on_hand_qty = StockQuant._get_available_quantity(product, location)

            line_vals.append({
                'request_id': self.id,
                'product_id': product.id,
                'order_qty': 0.0,
                'on_hand_qty': on_hand_qty,
                'product_qty': 0.0,
            })

        if line_vals:
            self.env['manufacturing.request.line'].create(line_vals)

        self.state = 'confirmed'

    def action_create_manufacturing_orders(self):
        """Server Action: Create MOs from request lines"""
        mo_obj = self.env["mrp.production"]
        # picking_obj = self.env["stock.picking"]

        for line in self.line_ids:
            dest_location = self.branch_id.lot_stock_id

            if line.product_qty > 0:
                mo = mo_obj.create({
                    "product_id": line.product_id.id,
                    "product_qty": line.product_qty,
                    'date_start': self.date,
                    'user_id': self.env.user.id,
                    'company_id': self.env.company.id,
                    'branch_id': self.branch_id.id,
                })
                mo.action_confirm()
                line.mrp_production_id = mo

                source_location = mo.location_dest_id if mo.location_dest_id else False

                if not source_location or not dest_location:
                    continue  # skip if locations not defined

                picking_vals = {
                    "picking_type_id": mo.picking_type_id.id,
                    "location_id": source_location.id,
                    "location_dest_id": dest_location.id,
                    "origin": self.name,
                    "scheduled_date": self.date,
                    "state": "waiting",
                    "move_ids_without_package": [(0, 0, {
                        "name": line.product_id.display_name,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.product_qty,
                        "product_uom": line.product_id.uom_id.id,
                        "location_id": source_location.id,
                        "location_dest_id": dest_location.id,
                    })],
                }
                picking_obj.create(picking_vals)

        self.state = "done"
