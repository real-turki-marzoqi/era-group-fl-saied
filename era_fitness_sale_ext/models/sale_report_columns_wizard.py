# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleReportColumnsWizard(models.TransientModel):
    _name = "sale.report.columns.wizard"
    _description = "Choose Columns for Quotation Report"

    sale_id = fields.Many2one('sale.order', required=True)

    show_brand = fields.Boolean(default=True)
    show_warranty = fields.Boolean(default=True)
    show_qty = fields.Boolean(string="Quantity", default=True)
    show_discount = fields.Boolean(string="Discount", default=True)
    show_amount = fields.Boolean(string="Amount", default=True)
    show_image = fields.Boolean(string="Image", default=True)

    def action_print(self):
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ctx.update({
            'show_brand': self.show_brand,
            'show_warranty': self.show_warranty,
            'show_qty': self.show_qty,
            'show_discount': self.show_discount,
            'show_amount': self.show_amount,
            'show_image': self.show_image,
        })
        return self.env.ref('sale.action_report_saleorder').with_context(ctx).report_action(self.sale_id, config=False)
