__author__ = 'trananhdung17'

from openerp import models, fields, api
from openerp.tools.translate import _

class stock_location(models.Models):
    _name = 'stock.location'

    name = fields.Char(string='Name')
    address_street = fields.Char(string='Street')
    address_state = fields.Char(string='State')
    address_city = fields.Char(string='City')
    country = fields.Many2one(comodel_name='res.country', string='Country')
    quantity_ids = fields.One2many(comodel_name='stock.quantity', inverse_name='location_id',string='Products Quantity')

class stockk_location_quantity(models.Model):
    _name = 'stock.quantity'

    name = fields.Char(string='Description')
    product_id = fields.Many2one(comodel_name='product.template', string='Product', required=True)
    product_qty = fields.Integer(string='Quantity')