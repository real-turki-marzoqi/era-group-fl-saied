# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_saved = fields.Boolean(string="Saved Location",
                              help="Mark this location as Saved / أمانات location.")
