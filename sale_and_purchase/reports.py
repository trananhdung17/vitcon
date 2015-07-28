__author__ = 'trananhdung17'

from openerp import models, fields, api
import time

class sale_report(models.TransientModel):
    _name = 'ir.report.sales'

    @api.multi
    @api.depends('item_ids')
    def _compute_total_amount(self):
        for r in self:
            total_amount = 0.00
            for item in r.item_ids:
                total_amount += item.amount
            r.total_amount = total_amount

    name = fields.Char(string='Name')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    state = fields.Selection([('all', 'All (exclude Cancelled)'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('shipping', 'Shipping'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done')], default='all', required=True, string='Order State')
    sale_type = fields.Selection([('all', 'All'),
        ('order', 'Pre-Order'),
        ('direct', 'Direct')], default='all', required=True, string='Sale Type')
    item_ids = fields.One2many(comodel_name='report.sale.item', inverse_name='report_id', string='Details')
    total_amount = fields.Float(string='Total Amount', compute=_compute_total_amount)

    @api.multi
    def action_report_render(self):
        itemObject = self.env['report.sale.item']
        itemObject.search([('report_id', '=', self.id)]).unlink()
        start_date = self.start_date or '0001-01-01'
        end_date = self.end_date or '9999-12-31'
        query = '''
            select o.id
            from sale_order as o
            where 	not (('%s'::date > o.order_date) or ('%s'::date < o.order_date))
        ''' %(start_date, end_date)
        if self.state in ['draft', 'confirmed', 'shipping', 'done', 'cancelled']:
            query += " and o.state = '%s' " %(self.state)
        else:
            query += " and o.state != 'cancelled' "
        if self.sale_type in ['order', 'direct']:
            query += " and o.type = '%s' " %(self.sale_type)
        query += ' order by o.order_date'
        self.env.cr.execute(query)
        data = self.env.cr.fetchall()
        for d in data:
            vals = {
                'order_id': d[0],
                'report_id': self.id
            }
            itemObject.create(vals)
        view = self.env.ref('sale_and_purchase.view_report_sale_config')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Report',
            'res_model': 'ir.report.sales',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
            'view_id': view.id
        }

    @api.multi
    def action_render_report(self):
        pass

class report_sale_item(models.TransientModel):
    _name = 'report.sale.item'

    report_id = fields.Many2one(comodel_name='ir.report.sales', string='Report')
    order_id = fields.Many2one(comodel_name='sale.order', string='Order No.')
    customer = fields.Char(string='Customer', related='order_id.customer')
    order_date = fields.Date(string='Order Date', related='order_id.order_date')
    amount = fields.Float(stringn='Amount', related='order_id.total_amount')
    state = fields.Selection([('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('shipping', 'Shipping'),
        ('done', 'Done'), ('cancelled', 'Cancelled')], string='State', related='order_id.state')

class purchase_report(models.TransientModel):
    _name = 'ir.report.purchases'

    @api.multi
    @api.depends('item_ids')
    def _compute_total_amount(self):
        for r in self:
            total_amount = 0.00
            for item in r.item_ids:
                total_amount += item.amount
            r.total_amount = total_amount

    name = fields.Char(string='Report Name')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    state = fields.Selection([('all', 'All (exclude Cancelled)'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')], default='all', required=True, string='Order State')
    item_ids = fields.One2many(comodel_name='report.purchase.item', inverse_name='report_id', string='Details')
    total_amount = fields.Float(string='Total Amount', compute=_compute_total_amount)

    @api.multi
    def action_report_render(self):
        itemObject = self.env['report.purchase.item']
        itemObject.search([('report_id', '=', self.id)]).unlink()
        start_date = self.start_date or '0001-01-01'
        end_date = self.end_date or '9999-12-31'
        query = '''
            select o.id
            from purchase_order as o
            where not (('%s'::date > o.purchase_date) or ('%s'::date < o.purchase_date))
        ''' %(start_date, end_date)
        if self.state in ['draft', 'confirmed', 'done', 'cancelled']:
            query += " and o.state = '%s' " %(self.state)
        else:
            query += " and o.state != 'cancelled' "
        query += ' order by o.purchase_date'
        self.env.cr.execute(query)
        data = self.env.cr.fetchall()
        for d in data:
            vals = {
                'order_id': d[0],
                'report_id': self.id
            }
            itemObject.create(vals)
        view = self.env.ref('sale_and_purchase.view_report_purchase_config')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.report.purchases',
            'name': 'Purchases Report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
            'view_id': view.id
        }

    @api.multi
    def action_render_report(self):
        pass

class report_purchase_item(models.TransientModel):
    _name = 'report.purchase.item'

    report_id = fields.Many2one(comodel_name='ir.report.purchases', string='Report')
    order_id = fields.Many2one(comodel_name='purchase.order', string='Order No.')
    supplier = fields.Many2one(comodel_name='res.partner', related='order_id.partner_id')
    order_date = fields.Date(string='Purchase Date', related='order_id.purchase_date')
    amount = fields.Float(stringn='Amount', related='order_id.total_amount')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                             string='State', related='order_id.state')
