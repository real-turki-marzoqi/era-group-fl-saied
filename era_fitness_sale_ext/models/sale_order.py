# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
from ast import literal_eval

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ("rq", "Request Quotation"),
        ("quotation_review", "Quotation Review"),
        ("draft", "Quotation"),
        ("sent", "Quotation Sent"),
        ("confirm", "Confirmed"),
        ("sale", "Sales Order"),
        ("done", "Locked"),
        ("cancel", "Cancelled"),
    ], string="Status", readonly=True, copy=False, index=True, default="rq", tracking=3)

    quotation_category_id = fields.Many2one(
        "product.category",
        string="Category",
        domain=[("appear_in_quotation", "=", True)],
        help='Only categories with "Appear in a Quotation" enabled are selectable.',
    )

    quotation_type = fields.Selection([
        ("supply", "Supply"),
        ("installation", "Installation"),
        ("supply_installation", "Supply & Installation"),
    ], string="Quotation Type")

    q_type = fields.Selection([
        ("cash", "Cash Quotation"),
        ("forward", "Forward Quotation"),
        ("tender", "Tender"),
    ], string="Type")

    bid_closing_date = fields.Date(string="Bid Closing Date")

    # ===== تتبع موافقات مرحلة المراجعة =====
    review_manager_approved = fields.Boolean(string="Mgr Approved", default=False, readonly=True, tracking=True)
    review_manager_id = fields.Many2one("res.users", string="Mgr Approver", readonly=True, tracking=True)
    review_manager_date = fields.Datetime(string="Mgr Approved On", readonly=True, tracking=True)

    review_coord_approved = fields.Boolean(string="Coordinator Approved", default=False, readonly=True, tracking=True)
    review_coord_id = fields.Many2one("res.users", string="Coordinator Approver", readonly=True, tracking=True)
    review_coord_date = fields.Datetime(string="Coordinator Approved On", readonly=True, tracking=True)

    review_admin_approved = fields.Boolean(string="Sales Admin Approved", default=False, readonly=True, tracking=True)
    review_admin_id = fields.Many2one("res.users", string="Sales Admin Approver", readonly=True, tracking=True)
    review_admin_date = fields.Datetime(string="Sales Admin Approved On", readonly=True, tracking=True)

    @api.constrains('q_type', 'bid_closing_date')
    def _check_bid_closing_date_required(self):
        for order in self:
            if order.q_type == 'tender' and not order.bid_closing_date:
                raise ValidationError(_("Bid Closing Date is required when Quotation Type is Tender."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("state", "rq")
            vals.setdefault("name", "/")
        return super().create(vals_list)

    # ========== تدفّق Request Quotation ==========
    def action_submit_request(self):
        for order in self:
            if order.state not in ("draft", "rq"):
                raise UserError(_("You can only move to Request Quotation from Draft or if already rq."))
            order.state = "rq"
            order.message_post(
                body=_("📤 Sent to *Request Quotation* by %s.") % self.env.user.name,
                subtype_xmlid="mail.mt_comment",
            )

    def action_approve_request(self):
        if not self.env.user.has_group("era_fitness_sale_ext.group_sale_request_approver"):
            raise AccessError(_("You are not allowed to approve Request Quotation."))
        for order in self:
            if order.state != "rq":
                raise UserError(_("Only Request Quotation can be approved."))
            order.write({
                "state": "quotation_review",
                "review_manager_approved": False,
                "review_manager_id": False,
                "review_manager_date": False,
                "review_coord_approved": False,
                "review_coord_id": False,
                "review_coord_date": False,
                "review_admin_approved": False,
                "review_admin_id": False,
                "review_admin_date": False,
            })
            order.message_post(
                body=_("📝 Moved to *Quotation Review* by %s.") % self.env.user.name,
                subtype_xmlid="mail.mt_comment",
            )

    # ========== Confirm قبل Sales Order ==========
    def action_set_confirm(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError(_("You can only set Confirm from Quotation or Quotation Sent."))
            order.state = "confirm"
            order.message_post(
                body=_("✅ Set to *Confirm* by %s.") % self.env.user.name,
                subtype_xmlid="mail.mt_comment",
            )

    def action_confirm(self):
        """
        عندما تكون الحالة = confirm:
        - نحولها مؤقتًا إلى draft لأن ديفولت أودو يسمح بالتأكيد من draft/sent فقط.
        - نستدعي super().action_confirm() ليتم إنشاء SO وتغيير الحالة إلى sale.
        - نسجّل رسالة في الشاتر.
        """
        # تأكد أن كل السجلات في confirm حتى لا تظهر رسالة Odoo الافتراضية
        to_force = self.filtered(lambda o: o.state == "confirm")
        if len(to_force) != len(self):
            # لو في سجلات خارج confirm نعطي رسالة واضحة
            raise UserError(_("Some orders are not in Confirm state. Move them to Confirm first."))

        # ارجاع المؤكدين مؤقتاً إلى draft
        to_force.write({'state': 'draft'})

        # استدعاء السلوك القياسي مع الـ context المطلوب (مثل validate_analytic)
        res = super(SaleOrder, to_force.with_context(validate_analytic=True)).action_confirm()

        # رسالة شاتر بعد التأكيد الناجح
        for order in to_force:
            if order.state == "sale":
                order.message_post(
                    body=_("🧾 *Sales Order* confirmed by %s.") % self.env.user.name,
                    subtype_xmlid="mail.mt_comment",
                )

        return res

    # ========== موافقات Quotation Review ==========
    def _is_current_user_direct_manager(self):
        self.ensure_one()
        try:
            emp = self.env["hr.employee"].sudo().search([("user_id", "=", self.user_id.id)], limit=1)
            if emp and emp.parent_id and emp.parent_id.user_id:
                return emp.parent_id.user_id.id == self.env.user.id
        except Exception:
            return False
        return False

    def action_review_approve_manager(self):
        for order in self:
            if order.state != "quotation_review":
                raise UserError(_("Approval only in Quotation Review."))
            if not order._is_current_user_direct_manager():
                raise AccessError(_("Only the direct manager of the salesperson can approve this step."))
            order.write({
                "review_manager_approved": True,
                "review_manager_id": self.env.user.id,
                "review_manager_date": fields.Datetime.now(),
            })
            order.message_post(
                body=_("👤 *Manager Approval* by %s.") % self.env.user.name,
                subtype_xmlid="mail.mt_comment",
            )

    def action_review_approve_coordinator(self):
        if not self.env.user.has_group("era_fitness_sale_ext.group_sale_order_coordinator"):
            raise AccessError(_("Only Sales Coordinator can approve this step."))
        for order in self:
            if order.state != "quotation_review":
                raise UserError(_("Approval only in Quotation Review."))
            order.write({
                "review_coord_approved": True,
                "review_coord_id": self.env.user.id,
                "review_coord_date": fields.Datetime.now(),
            })
            order.message_post(
                body=_("📌 *Coordinator Approval* by %s.") % self.env.user.name,
                subtype_xmlid="mail.mt_comment",
            )

    def action_review_approve_admin(self):
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            raise AccessError(_("Only Sales Admin can approve this step."))
        for order in self:
            if order.state != "quotation_review":
                raise UserError(_("Approval only in Quotation Review."))
            order.write({
                "review_admin_approved": True,
                "review_admin_id": self.env.user.id,
                "review_admin_date": fields.Datetime.now(),
            })
            order.message_post(
                body=_("🔐 *Sales Admin Approval* by %s.") % self.env.user.name,
                subtype_xmlid="mail.mt_comment",
            )

    def action_review_finalize(self):
        for order in self:
            if order.state != "quotation_review":
                raise UserError(_("Finalize only in Quotation Review."))
            if not (order.review_manager_approved and order.review_coord_approved and order.review_admin_approved):
                raise UserError(_("All three approvals are required before finalizing."))
            old_name = order.name
            if order.name in (False, "/"):
                order.name = self.env["ir.sequence"].next_by_code("sale.order") or "/"
            order.state = "draft"
            order.message_post(
                body=_("✅ *Review Finalized* by %s → state set to *Quotation* (name: %s → %s).") %
                     (self.env.user.name, old_name or "/", order.name),
                subtype_xmlid="mail.mt_comment",
            )

    # ===== بقية أكوادك كما هي (onchange + catalog) =====
    @api.onchange('quotation_category_id')
    def _onchange_quotation_category_id_cleanup_lines(self):
        for order in self:
            qcat = order.quotation_category_id
            _logger.warning(
                "[RQ] order#%s quotation_category changed to %s -> checking lines",
                order.id or 'new', qcat.id if qcat else None
            )
            qcat_child_ids = set()
            if qcat:
                qcat_child_ids = set(order.env['product.category'].search([('id', 'child_of', qcat.id)]).ids)

            for line in order.order_line:
                if qcat and line.line_categ_id:
                    in_tree = line.line_categ_id.id in qcat_child_ids
                    if not in_tree:
                        line.line_categ_id = False
                        if line.product_template_id:
                            line.product_template_id = False
                        if line.product_id:
                            line.product_id = False

                base_categ = line.line_categ_id or qcat
                if base_categ:
                    if line.product_template_id:
                        tmpl_ok = bool(order.env['product.category'].search_count([
                            ('id', 'child_of', base_categ.id),
                            ('id', '=', line.product_template_id.categ_id.id),
                        ]))
                        if not tmpl_ok:
                            line.product_template_id = False
                            if line.product_id:
                                line.product_id = False
                    elif line.product_id:
                        prod_ok = bool(order.env['product.product'].search_count([
                            ('id', '=', line.product_id.id),
                            ('categ_id', 'child_of', base_categ.id),
                        ]))
                        if not prod_ok:
                            line.product_id = False

    def _merge_context(self, base_ctx, extra_ctx):
        ctx = {}
        if isinstance(base_ctx, dict):
            ctx = dict(base_ctx)
        elif isinstance(base_ctx, str):
            try:
                parsed = literal_eval(base_ctx)
                if isinstance(parsed, dict):
                    ctx = dict(parsed)
            except Exception:
                ctx = {}
        ctx.update(extra_ctx or {})
        return ctx

    def action_add_from_catalog(self):
        self.ensure_one()
        res = super().action_add_from_catalog()
        if not isinstance(res, dict):
            return res

        has_cat = bool(self.quotation_category_id)
        extra_ctx = {
            'catalog_categ_id': self.quotation_category_id.id if has_cat else 0,
            'searchpanel_default_categ_id': self.quotation_category_id.id if has_cat else False,
            'search_default_no_products': 0 if has_cat else 1,
        }
        extra_domain = [('categ_id', 'child_of', self.quotation_category_id.id)] if has_cat else [('id', '=', 0)]

        res['context'] = self._merge_context(res.get('context', {}), extra_ctx)

        existing_domain = res.get('domain')
        if existing_domain:
            res['domain'] = ['&'] + (existing_domain if isinstance(existing_domain, list) else [existing_domain]) + extra_domain
        else:
            res['domain'] = extra_domain
        return res
