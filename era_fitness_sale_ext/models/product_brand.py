# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _order = "name"
    _rec_name = "name"

    name = fields.Char(string="Brand Name", required=True, translate=False, index=True)
    code = fields.Char(string="Code", help="Short code for the brand", index=True)
    logo = fields.Binary(string="Logo")
    website = fields.Char(string="Website")
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description")

    product_count = fields.Integer(
        string="Products",
        compute="_compute_product_count",
        store=False
    )

    warranty_period = fields.Integer(
        string="Warranty Period (Months)",
        help="Warranty duration in months for this brand."
    )

    _sql_constraints = [
        ("brand_name_uniq", "unique(name)", "Brand name must be unique!"),
        ("brand_code_uniq", "unique(code)", "Brand code must be unique!"),
    ]

    @api.depends()
    def _compute_product_count(self):
        data = self.env["product.template"].read_group(
            [("brand_id", "in", self.ids)], ["brand_id"], ["brand_id"]
        )
        mapped = {d["brand_id"][0]: d["brand_id_count"] for d in data if d.get("brand_id")}
        for rec in self:
            rec.product_count = mapped.get(rec.id, 0)

    def action_view_products(self):
        self.ensure_one()
        action = self.env.ref("product.product_template_action").read()[0]
        action["domain"] = [("brand_id", "=", self.id)]
        action["context"] = {"default_brand_id": self.id}
        return action
