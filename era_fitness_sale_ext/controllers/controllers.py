# -*- coding: utf-8 -*-
# from odoo import http


# class EraFitnessSaleExt(http.Controller):
#     @http.route('/era_fitness_sale_ext/era_fitness_sale_ext', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/era_fitness_sale_ext/era_fitness_sale_ext/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('era_fitness_sale_ext.listing', {
#             'root': '/era_fitness_sale_ext/era_fitness_sale_ext',
#             'objects': http.request.env['era_fitness_sale_ext.era_fitness_sale_ext'].search([]),
#         })

#     @http.route('/era_fitness_sale_ext/era_fitness_sale_ext/objects/<model("era_fitness_sale_ext.era_fitness_sale_ext"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('era_fitness_sale_ext.object', {
#             'object': obj
#         })

