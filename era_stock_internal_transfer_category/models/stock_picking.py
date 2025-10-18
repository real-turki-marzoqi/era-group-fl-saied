from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    with_category = fields.Boolean(
        string="Use Product Category",
        compute='_compute_with_category',
        store=True,
        help="If checked, product lines will be filtered by selected categories."
    )

    @api.depends('picking_type_id')
    def _compute_with_category(self):
        for rec in self:
            rec.with_category = True if rec.picking_type_id.code == 'internal' else False


# domain="[('bom_ids', '!=', False)]"