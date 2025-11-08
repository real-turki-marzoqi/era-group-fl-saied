# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = "crm.lead"

    # تصنيف رئيسي يحدد نطاق المنتجات
    product_category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        help="Only products under this category (and its children) will be selectable."
    )

    @api.constrains('product_category_id')
    def _check_product_category_allowed(self):
        for rec in self:
            cat = rec.product_category_id
            if cat and not getattr(cat, 'appear_in_crm', False):
                raise ValidationError(_("Selected category is not allowed for CRM (appear_in_crm is False)."))

    # مجموعة المنتجات (variants)
    product_ids = fields.Many2many(
        "product.product",
        "crm_lead_product_rel",
        "lead_id",
        "product_id",
        string="Products",
        help="Pick products under the selected category (and its child categories).",
        domain="[('categ_id', 'child_of', product_category_id)]",
    )

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        """فلترة الخيارات + تنظيف أي منتجات خارج التصنيف المختار وأبنائه."""
        for rec in self:
            domain = [('categ_id', 'child_of', rec.product_category_id.id)] if rec.product_category_id else []
            # تنظيف المنتجات الخارجة عن النطاق
            if rec.product_ids and rec.product_category_id:
                allowed = rec.env['product.product'].search(domain).ids
                rec.product_ids = rec.product_ids.filtered(lambda p: p.id in allowed)
            # إرجاع دومين ديناميكي للواجهة
            return {'domain': {'product_ids': domain}}
