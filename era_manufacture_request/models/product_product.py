# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_finished_good = fields.Boolean("Finished Good")
