# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    x_vendor_lead_days = fields.Integer(
        string='Vendor own lead time (days)',
    )
    x_transit_min = fields.Integer(
        string='Transit to us min (days)',
    )
    x_transit_max = fields.Integer(
        string='Transit to us max (days)',
    )
    x_offer_source = fields.Selection(
        [('stock', 'From vendor stock'),
         ('leadtime', 'Vendor lead time'),
         ('backorder', 'Backorder / ETA unknown')],
        string='Offer type',
    )
    x_lead_total = fields.Char(
        string='Lead time to publish',
        compute='_compute_lead_total',
        store=False,
    )

    @api.depends('x_vendor_lead_days', 'x_transit_min', 'x_transit_max')
    def _compute_lead_total(self):
        for record in self:
            v = record.x_vendor_lead_days or 0
            tmin = record.x_transit_min or 0
            tmax = record.x_transit_max or 0
            if v + tmax:
                record.x_lead_total = '%d-%d Days' % (v + tmin, v + tmax)
            else:
                record.x_lead_total = ''
