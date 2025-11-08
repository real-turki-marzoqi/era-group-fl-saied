# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    line_categ_id = fields.Many2one(
        "product.category",
        string="Line Category",
        help=_("Restrict products to this category and its children."),
    )
    product_image_128 = fields.Image(
        string="Image",
        related="product_template_id.image_128",
        readonly=True,
    )

    brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
        related="product_template_id.brand_id",
        store=True,
        readonly=True,
    )

    # الضمان (أشهر) ريد أونلي حسب البراند عبر المنتج
    warranty_period = fields.Integer(
        string="Warranty Period (Months)",
        related="product_template_id.warranty_period",
        readonly=True,
        store=True,
        help="Read-only. Inherited from the product's brand."
    )

    @api.onchange("line_categ_id")
    def _onchange_line_categ_product_domain(self):
        self.ensure_one()
        qcat = self.order_id.quotation_category_id
        if qcat and self.line_categ_id:
            in_tree = bool(self.env["product.category"].search_count([
                ("id", "child_of", qcat.id),
                ("id", "=", self.line_categ_id.id),
            ]))
            if not in_tree:
                self.line_categ_id = False
                if self.product_template_id:
                    self.product_template_id = False
                if self.product_id:
                    self.product_id = False
                return {"domain": {"product_template_id": []}}

        if self.product_template_id:
            self.product_template_id = False
        if self.product_id:
            self.product_id = False

        domain = [("categ_id", "child_of", self.line_categ_id.id)] if self.line_categ_id else []
        return {"domain": {"product_template_id": domain}}

    @api.constrains("line_categ_id", "product_template_id", "order_id", "order_id.quotation_category_id")
    def _check_product_belongs_to_line_category(self):
        for line in self:
            qcat = line.order_id.quotation_category_id
            if qcat and line.line_categ_id:
                ok_line_categ = bool(self.env["product.category"].search_count([
                    ("id", "child_of", qcat.id),
                    ("id", "=", line.line_categ_id.id),
                ]))
                if not ok_line_categ:
                    raise ValidationError(_("Line Category must match the Quotation Category or one of its children."))

            if not line.line_categ_id or not line.product_template_id:
                continue

            ok_prod = bool(self.env["product.category"].search_count([
                ("id", "child_of", line.line_categ_id.id),
                ("id", "=", line.product_template_id.categ_id.id),
            ]))
            if not ok_prod:
                raise ValidationError(_("Selected product does not belong to the chosen Line Category."))
