# -*- coding: utf-8 -*-
{
    "name": "Era Fitness Sale Ext",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Adds 'Request Quotation' pre-quotation flow + Product Brands field & menu",
    "author": "Era Group | Developer : Turki Marzoqi",
    "website": "https://personal-page-gray.vercel.app/",
    "license": "LGPL-3",
    "depends": [
        "sale_management",   # نحتاجه عشان منيو sale.product_menu_catalog
        "product"
    ],
    "data": [
        # أولوية الأمن أولاً
        "security/groups.xml",
        "security/ir.model.access.csv",

        # الفيوز
        "views/sale_order_views.xml",
        "views/product_category_views.xml",
        "views/product_brand_views.xml",
        "views/product_template_views.xml",
        "views/report_saleorder_inherit_brand.xml",
        "views/sale_report_columns_wizard_views.xml",
        "views/crm_lead_view.xml",
    ],
    "installable": True,
    "application": False,
}
