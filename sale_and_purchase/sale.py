__author__ = 'trananhdung17'

from openerp import models, api, fields
from openerp.exceptions import ValidationError, Warning

class sale_order(models.Model):
    _inherit = ['mail.thread']
    _name = 'sale.order'
    _table = 'sale_order'
    _order = 'order_date desc'

    @api.multi
    @api.depends('order_line_ids')
    def compute_amount_total(self):
        for r in self:
            total_amount = 0
            for line in r.order_line_ids:
                total_amount += line.subtotal
            r.total_amount = total_amount

    @api.model
    def get_default_name(self):
        sequence = self.env.ref('sale_and_purchase.sequence_sale_order')
        return sequence.next_by_id(sequence.id)

    @api.multi
    @api.depends('customer_name', 'partner_id', 'customer_address')
    def _get_customer_name(self):
        for r in self:
            if r.partner_id:
                r.customer = r.partner_id.name
            else:
                r.customer = r.customer_name or r.customer_address

    name = fields.Char(string='Order No.', default=get_default_name, readonly=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer')
    customer_name = fields.Char(string='Customer')
    customer_address = fields.Char(string='Address')
    customer_phone = fields.Char(string='Phone')
    customer = fields.Char(string='Customer', compute=_get_customer_name)
    order_date = fields.Date(string='Order Date', required=True)
    sale_date = fields.Date(string='Delivery Date')
    order_line_ids = fields.One2many(comodel_name='sale.order.line', inverse_name='order_id', string='Order Lines')
    type = fields.Selection([('order', 'Pre-Order'),('direct','Direct')], string='Sale Type')
    state = fields.Selection([('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('shipping', 'Shipping'),
        ('done', 'Done'), ('cancelled', 'Cancelled')], string='Status', default='draft')
    total_amount = fields.Float(string='Amount Total', compute=compute_amount_total)
    shipping_amount = fields.Float(string='Shipping Amount')
    notes = fields.Text(string='Notes')

    @api.multi
    def button_confirm(self):
        for r in self:
            if r.total_amount <= 0:
                raise Warning('Warning! You cannot confirm order without order line or amount = 0')
            if r.state == 'draft':
                r.state = 'confirmed'

    @api.multi
    def button_shipping(self):
        for r in self:
            if r.total_amount <= 0:
                raise Warning('Warning! You cannot ship order without order line or amount = 0')
            if r.state in ['draft', 'confirmed']:
                r.state = 'shipping'
                if not r.sale_date:
                    r.sale_date = r.order_date

    @api.multi
    def button_done(self):
        for r in self:
            if r.state in ['confirmed', 'shipping']:
                r.state = 'done'

    @api.multi
    def action_cancel(self):
        for r in self:
            if r.state in ['draft', 'confirmed']:
                r.state = 'cancelled'

    @api.model
    def create(self, vals):
        if self.env.context.get('default_type', False) == 'direct' or vals.get('type', False) == 'direct':
            vals.update({'state': 'done'})
        return super(sale_order, self).create(vals)

class sale_order_line(models.Model):
    _name = 'sale.order.line'

    @api.multi
    @api.depends('price', 'quantity')
    def compute_subtotal(self):
        for r in self:
            r.subtotal = r.price * r.quantity

    name = fields.Char(string='Description')
    order_id = fields.Many2one(comodel_name='sale.order', string='Order')
    product_id = fields.Many2one(comodel_name='product.template', required=True)
    code_product = fields.Char(string='Product Code', related='product_id.code', readonly=True)
    quantity = fields.Integer(string='Quantity', default=1)
    price = fields.Float(string='Price')
    subtotal = fields.Float(string='Subtotal', compute=compute_subtotal)

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.price = self.product_id.sale_price or self.product_id.standard_price
