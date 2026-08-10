# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_broker_status = fields.Selection(
        [('0', 'Not listed'), ('1', 'Lead time'), ('2', 'In stock')],
        string='Broker Status (BBN / TBS only)',
        default='0',
    )
    x_broker_qty = fields.Integer(
        string='Broker Listed Qty',
    )
    x_broker_price = fields.Float(
        string='Broker Sell Price (USD, BBN)',
        digits='Product Price',
    )
    x_broker_price_eur = fields.Float(
        string='Broker Sell Price (EUR, TBS)',
        digits='Product Price',
    )
    x_broker_desc = fields.Text(
        string='Broker Listing Description',
    )
    x_broker_lead_min = fields.Integer(
        string='Lead Time Min (days)',
    )
    x_broker_lead_max = fields.Integer(
        string='Lead Time Max (days)',
    )
    x_broker_lead_text = fields.Char(
        string='Lead time',
        compute='_compute_broker_lead_text',
        store=False,
    )
    x_bbn_listed = fields.Boolean(
        string='Listed on BrokerBin',
    )
    x_bbn_last_sync = fields.Date(
        string='BrokerBin Last Upload',
    )
    x_tbs_listed = fields.Boolean(
        string='Listed on TheBrokerSite',
    )
    x_tbs_last_sync = fields.Date(
        string='TheBrokerSite Last Upload',
    )
    x_product_brand_id = fields.Many2one(
        'x_product_brand',
        string='Brand',
    )

    @api.depends('x_broker_lead_min', 'x_broker_lead_max')
    def _compute_broker_lead_text(self):
        for record in self:
            mn = record.x_broker_lead_min or 0
            mx = record.x_broker_lead_max or 0
            if mx:
                if mn != mx:
                    record.x_broker_lead_text = '%d-%d days' % (mn, mx)
                else:
                    record.x_broker_lead_text = '%d days' % mx
            else:
                record.x_broker_lead_text = ''
