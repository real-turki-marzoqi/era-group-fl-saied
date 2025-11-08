# -*- coding: utf-8 -*-
from odoo import api, models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
        ondelete="restrict",
        index=True,
        help="Select the product brand."
    )

    # الضمان ريد أونلي حسب البراند
    warranty_period = fields.Integer(
        string="Warranty Period (Months)",
        related="brand_id.warranty_period",
        readonly=True,
        store=True,
        help="Read-only. Inherited from the selected brand."
    )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        line_categ_id = self._context.get('line_categ_id')
        if line_categ_id:
            args.append(('categ_id', 'child_of', line_categ_id))
        return super().name_search(name, args=args, operator=operator, limit=limit)

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        args = list(args or [])
        line_categ_id = self._context.get('line_categ_id')
        if line_categ_id:
            args.append(('categ_id', 'child_of', line_categ_id))
        return super().search(args, offset=offset, limit=limit, order=order)
