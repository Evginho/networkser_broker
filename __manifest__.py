# -*- coding: utf-8 -*-
{
    'name': 'Networkser Broker',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Broker platform integration fields (BrokerBin / TheBrokerSite)',
    'description': """
Broker channel fields and views for Networkser product listings.

Fields on product.template:
- Broker listing: status, qty, price (USD/EUR), description
- Lead time: min/max days, computed lead text
- Channel flags: BBN/TBS listed + last sync dates

Fields on product.supplierinfo:
- Vendor lead time + transit min/max
- Offer source type
- Computed lead total

Custom model:
- x_product_brand: product brand with name, slug, logo
    """,
    'author': 'Networkser Group BV',
    'website': 'https://networkser.com',
    'depends': ['product', 'purchase', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_supplierinfo_views.xml',
        'views/x_product_brand_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': '_create_external_ids',
}
