# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    days_normal = fields.Integer()
    days_middle = fields.Integer()
    days_weekday = fields.Integer()
