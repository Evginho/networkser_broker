# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductBrand(models.Model):
    _name = 'x_product_brand'
    _description = 'Product Brand'

    x_name = fields.Char(string='Name')
    x_slug = fields.Char(string='Slug')
    x_logo = fields.Binary(string='Logo')
