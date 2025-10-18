from odoo import models, fields, api
import json


class StockMove(models.Model):
    _inherit = 'stock.move'

    category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        help='Select a product category to filter available products.'
    )


    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends('category_id')
    def _compute_product_id_domain(self):
        for rec in self:
            rec.product_id_domain = json.dumps([])
            if rec.category_id:
                rec.product_id_domain = json.dumps(
                    [('categ_id', '=', rec.category_id.id)]
                )