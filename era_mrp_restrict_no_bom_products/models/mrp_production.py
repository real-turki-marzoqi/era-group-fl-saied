# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_id = fields.Many2one(
        'product.product', 'Product',
        compute='_compute_product_id', store=True, copy=True, precompute=True,
        domain=lambda self: self._domain_products_with_bom(),
        readonly=False, required=True, check_company=True)

    @api.model
    def _domain_products_with_bom(self):
        """Return domain for products having at least one BoM."""
        products_with_bom = self.env['mrp.bom'].search([]).mapped('product_tmpl_id.product_variant_ids')
        return [('id', 'in', products_with_bom.ids), ('type', '=', 'consu')]
