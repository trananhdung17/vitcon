__author__ = 'trananhdung17'

from openerp import models, fields, api
import time


class purchase_order(models.Model):
    _inherit = ['mail.thread']
    _name = 'purchase.order'
    _order = 'purchase_date desc'

    @api.multi
    @api.depends('order_line_ids')
    def compute_total_amount(self):
        for r in self:
            total_amount = 0.00
            for line in r.order_line_ids:
                total_amount += line.subtotal
            r.total_amount = total_amount

    @api.model
    def get_default_purchase_date(self):
        return time.strftime('%Y-%m-%d')

    @api.model
    def get_default_name(self):
        sequence = self.env.ref('sale_and_purchase.sequence_purchase_order')
        return sequence.next_by_id(sequence.id)

    name = fields.Char(string='Purchase No.', required=True, default=get_default_name, readonly=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Supplier', required=True)
    order_line_ids = fields.One2many(comodel_name='purchase.order.line', inverse_name='order_id')
    purchase_date = fields.Date(stringn='Order Date', default=get_default_purchase_date)
    receive_date = fields.Date(string='Receive Date')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancelled', 'Cancelled')],
                             string='Status', default='draft')
    total_amount = fields.Float(string='Amount Total', compute=compute_total_amount)
    notes = fields.Text(string='Notes')

    @api.multi
    def action_confirm(self):
        for r in self:
            if r.state == 'draft':
                r.state = 'confirmed'

    @api.multi
    def action_done(self):
        for r in self:
            if r.state in ['draft', 'confirmed']:
                r.state = 'done'

    @api.multi
    def action_cancel(self):
        for r in self:
            if r.state in ['draft', 'confirmed']:
                r.state = 'cancelled'

class purchase_order_line(models.Model):
    _name = 'purchase.order.line'

    @api.multi
    @api.depends('price', 'quantity')
    def compute_subtotal(self):
        for r in self:
            r.subtotal = r.price * r.quantity

    name = fields.Char(string='Description')
    product_id = fields.Many2one(comodel_name='product.template', string='Product', required=True)
    order_id = fields.Many2one(comodel_name='purchase.order', string='Order')
    product_code = fields.Char(string="Product Code", related='product_id.code')
    quantity = fields.Integer(string='Quantity', default=1)
    price = fields.Float(string='Price')
    subtotal = fields.Float(string='Subtotal', compute=compute_subtotal)