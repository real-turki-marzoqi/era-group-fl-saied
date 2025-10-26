# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    days_normal = fields.Integer(related='company_id.days_normal', readonly=False)
    days_middle = fields.Integer(related='company_id.days_middle', readonly=False)
    days_weekday = fields.Integer(related='company_id.days_weekday', readonly=False)
