# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "analytic.mixin"]

    analytic_distribution = fields.Json(
        'Analytic Distribution',
        compute="_compute_analytic_distribution",
        inverse='_inverse_analytic_distribution'
    )

    @api.depends('move_ids_without_package')
    def _compute_analytic_distribution(self):
        for line in self:
            merged = defaultdict(float)

            # mapped may return list of dicts OR list of False → filter
            for dist in line.move_ids_without_package.mapped('analytic_distribution'):
                if isinstance(dist, dict):
                    for key, value in dist.items():
                        merged[key] += value

            # must assign a dict, not a list
            line.analytic_distribution = dict(merged)

    def _inverse_analytic_distribution(self):
        """If analytic distribution is set on move, write it on all move lines"""
        pass
