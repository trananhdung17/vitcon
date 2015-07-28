__author__ = 'trananhdung17'

from openerp import models, fields, api, tools
from openerp.exceptions import ValidationError, Warning

class product_template(models.Model):
    _inherit = ['mail.thread']
    _name = 'product.template'
    _order = 'code'

    @api.multi
    @api.depends('sale_pricelist_id')
    def compute_sale_price(self):
        for r in self:
            if r.sale_pricelist_id:
                for item in r.sale_pricelist_id.item_ids:
                    if item.product_id.id == r.id:
                        r.sale_price = item.price

    @api.multi
    @api.depends('purchase_pricelist_id')
    def compute_purchase_price(self):
        for r in self:
            if r.purchase_pricelist_id:
                for item in r.purchase_pricelist_id.item_ids:
                    if item.product_id.id == r.id:
                        r.purchase_price = item.price

    # @api.multi
    # @api.depends('image')
    # def _get_image(self):
    #     for r in self:
    #         r.image_medium = tools.image_get_resized_images(r.image, avoid_resize_medium=True)

    name = fields.Char(string='Product Name', required=True)
    code = fields.Char(string='Code')
    image = fields.Binary(string='Image')
    # image_medium = fields.Binary(string='Image', compute=_get_image)
    active = fields.Boolean(string='Active', default=True)
    category_id = fields.Many2one(comodel_name='product.category', string='Category')
    standard_price = fields.Float(string='Standard Price')
    purchase_price = fields.Float(string='Purchase Price', compute=compute_purchase_price, readonly=True)
    sale_price = fields.Float(string='Sale Price', compute=compute_sale_price, readonly=True)
    sale_pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Sale Pricelist')
    purchase_pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Purchase Pricelist')
    description = fields.Char(string='Description')
    priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string='Priority')
    standard_uom = fields.Many2one(comodel_name='product.uom', string='Standard UOM')

    @api.model
    def create(self, vals):
        # if vals.get('image'):
        #     vals['image'] = tools.image_get_resized_images(vals['image'], avoid_resize_medium=True)
        res = super(product_template, self).create(vals)
        all_sale_pricelist = self.env['product.pricelist'].search([('type', 'in', ['sale', 'purchase'])])
        item_model = self.env['product.pricelist.item']
        for l in all_sale_pricelist:
            item = item_model.create({
                'product_id': res.id,
                'price': res.standard_price,
                'pricelist_id': l.id
            })
        return res

    @api.multi
    def write(self, vals):
        # if vals.get('image'):
        #     vals['image'] = tools.image_get_resized_images(vals['image'], avoid_resize_medium=True)
        return super(product_template, self).write(vals)

    @api.multi
    def unlink(self):
        self.env['product.pricelist.item'].search([('product_id', 'in', [r.id for r in self])]).unlink()
        return super(product_template, self).unlink()

class product_category(models.Model):
    _name = 'product.category'
    _inherit = ['mail.thread']

    name = fields.Char(string='Category Name')
    active = fields.Boolean(string='Active', default=True)
    product_ids = fields.One2many(comodel_name='product.template', inverse_name='category_id', string='Products')
    parent_id = fields.Many2one(comodel_name='product.category', string='Parent Category')

class producte_pricelist(models.Model):
    _name = 'product.pricelist'
    _inherit = ['mail.thread']

    name = fields.Char(string='Pricelist', required=True)
    active = fields.Boolean(string='Active', default=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    item_ids = fields.One2many(comodel_name='product.pricelist.item', inverse_name='pricelist_id')
    type = fields.Selection([('sale', 'Sale'),('purchase', 'Purchase')], string='Type')

    @api.model
    def default_get(self, fields_list):
        res = super(producte_pricelist, self).default_get(fields_list)
        all_products = self.env['product.template'].search([])
        items = []
        for p in all_products:
            item = {
                'product_id': p.id,
                'price': p.standard_price
            }
            items.append(item)
        res.update(item_ids=items)

class product_pricelist_item(models.Model):
    _name = 'product.pricelist.item'

    product_id = fields.Many2one(comodel_name='product.template', string='Product', required=True)
    product_code = fields.Char(string='Product Code', related='product_id.code', readonly=True)
    price = fields.Float(string='Price')
    pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Pricelist')

class product_uom(models.Model):
    _name = 'product.uom'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    rate = fields.Float(string='Rate')
    type = fields.Selection([('standard', 'Standard'), ('other', 'Other')], string='Type')
    category_id = fields.Many2one(comodel_name='product.uom.category', string='Category', domain=[('active', '=', True)])

    @api.constrains('rate', 'category_id')
    def constrain_rate_category(self):
        if not self.rate and self.category_id:
            raise ValidationError('Error! You cannot make a UOM of %s category without rate' %(self.category_id.name))

class product_uom_category(models.Model):
    _name = 'product.uom.category'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    uom_ids = fields.One2many(comodel_name='product.uom', inverse_name='category_id', string='UOMs')

class my_res_partner(models.Model):
    _inherit = 'res.partner'

    pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Pricelist')

# class view_current_pricelist(models.Model):
#     _name = 'view.current.pricelist'
#
#
#     def init(self, cr):
#         tools.drop_view_if_exists(cr, viewname='view_current_pricelist')
#         query = '''
#             create or replace view view_current_pricelist as (
#                 select 1 as id, s.id as sale_pricelist_id, p.id as purchase_procelist_id
#                 from (
#                     select * from product_pricelist
#                     where active = true
#                         and (not (end_date not null and end_date < now()::date) or (start_date not null or start_date > now()::date))
#                         and type = sale
#                 ) as s
#                 full outer join (
#                     select * from product_pricelist
#                     where active = true
#                         and (not (end_date not null and end_date < now()::date) or (start_date not null or start_date > now()::date))
#                         and type = purchase
#                 ) as p
#             )
#         '''
#
#         cr.execute()
