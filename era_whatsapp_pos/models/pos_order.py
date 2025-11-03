from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def action_era_sent_receipt_on_whatsapp(self, order_ids, phone, ticket_image=None, basic_image=False):
        order = self.browse(order_ids[0])
        if not order or not order.config_id.whatsapp_enabled or not order.config_id.receipt_template_id or not phone:
            return

        filename = 'Receipt-' + order.name + '.jpg'
        receipt = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': ticket_image,
            'res_model': 'pos.order',
            'res_id': order.ids[0],
            'mimetype': 'image/jpeg',
        })
        whatsapp_composer = self.env['whatsapp.composer'].with_context({'active_id': order.id}).create(
            {
                'attachment_id': receipt.id,
                'phone': phone,
                'wa_template_id': order.config_id.receipt_template_id.id,
                'res_model': 'pos.order'
            }
        )
        whatsapp_composer._send_whatsapp_template()
        order.mobile = phone
        if order.to_invoice and order.config_id.invoice_template_id:
            whatsapp_composer = self.env['whatsapp.composer'].with_context({'active_id': order.account_move.id}).create(
                {
                    'phone': phone,
                    'wa_template_id': order.config_id.invoice_template_id.id,
                    'res_model': 'account.move'
                }
            )
            whatsapp_composer._send_whatsapp_template(force_send_by_cron=True)
