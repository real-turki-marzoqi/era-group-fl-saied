# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"

    appear_in_quotation = fields.Boolean(string="Appear in a Quotation", default=False)
    appear_in_crm = fields.Boolean(string="Appear in CRM", default=False)
    manager_ids = fields.Many2many(
        "hr.employee",
        "product_category_manager_rel",  # اسم الجدول الوسيط
        "category_id",  # العمود المرتبط بالتصنيف
        "employee_id",  # العمود المرتبط بالموظف
        string="Category Managers",
        help="Select one or more employees responsible for this product category."
    )

    delivery_code = fields.Char(string="Delivery Code")
    installation_code = fields.Char(string="Installation Code")
    consultation_code = fields.Char(string="Consultation Code")


