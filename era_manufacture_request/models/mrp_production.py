# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    branch_id = fields.Many2one("stock.warehouse",
                                string="Branch")

    def action_branch_picking(self):
        self.ensure_one
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        action['domain'] = [('mrp_production_id', '=', self.id)]
        return action

