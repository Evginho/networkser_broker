# -*- coding: utf-8 -*-
"""
Post-install hook: create ir.model.data external IDs for existing DB records
and clean up old DB-only views superseded by this module.

This links Studio-created fields/models/views to the networkser_broker module
so they become git-backed and no longer DB-only.
"""
import logging
_logger = logging.getLogger(__name__)


def _create_external_ids(env):
    """Post-install hook.

    Phase 1: Create ir.model.data external IDs for existing field records
             and the x_product_brand ir.model entry.
    Phase 2: Delete old DB-only views that have been superseded by module XML
             views (9404-9409, 9300).
    """
    IrModelData = env['ir.model.data']
    module = 'networkser_broker'
    created = 0
    skipped = 0
    not_found = 0

    # ── Phase 1: External IDs for fields and ir.model ──
    EXTERNAL_ID_MAP = [
        # x_product_brand ir.model entry (Python model creates this; just link)
        ('ir.model', 'model_x_product_brand',
         [('model', '=', 'x_product_brand')]),

        # x_product_brand model fields
        ('ir.model.fields', 'field_x_product_brand__x_name',
         [('model', '=', 'x_product_brand'), ('name', '=', 'x_name')]),
        ('ir.model.fields', 'field_x_product_brand__x_slug',
         [('model', '=', 'x_product_brand'), ('name', '=', 'x_slug')]),
        ('ir.model.fields', 'field_x_product_brand__x_logo',
         [('model', '=', 'x_product_brand'), ('name', '=', 'x_logo')]),

        # product.template broker fields
        ('ir.model.fields', 'field_product_template__x_broker_status',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_status')]),
        ('ir.model.fields', 'field_product_template__x_broker_qty',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_qty')]),
        ('ir.model.fields', 'field_product_template__x_broker_price',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_price')]),
        ('ir.model.fields', 'field_product_template__x_broker_price_eur',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_price_eur')]),
        ('ir.model.fields', 'field_product_template__x_broker_desc',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_desc')]),
        ('ir.model.fields', 'field_product_template__x_broker_lead_min',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_lead_min')]),
        ('ir.model.fields', 'field_product_template__x_broker_lead_max',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_lead_max')]),
        ('ir.model.fields', 'field_product_template__x_broker_lead_text',
         [('model', '=', 'product.template'), ('name', '=', 'x_broker_lead_text')]),
        ('ir.model.fields', 'field_product_template__x_bbn_listed',
         [('model', '=', 'product.template'), ('name', '=', 'x_bbn_listed')]),
        ('ir.model.fields', 'field_product_template__x_bbn_last_sync',
         [('model', '=', 'product.template'), ('name', '=', 'x_bbn_last_sync')]),
        ('ir.model.fields', 'field_product_template__x_tbs_listed',
         [('model', '=', 'product.template'), ('name', '=', 'x_tbs_listed')]),
        ('ir.model.fields', 'field_product_template__x_tbs_last_sync',
         [('model', '=', 'product.template'), ('name', '=', 'x_tbs_last_sync')]),
        ('ir.model.fields', 'field_product_template__x_product_brand_id',
         [('model', '=', 'product.template'), ('name', '=', 'x_product_brand_id')]),
        ('ir.model.fields', 'field_product_template__x_mpn',
         [('model', '=', 'product.template'), ('name', '=', 'x_mpn')]),

        # product.supplierinfo broker fields
        ('ir.model.fields', 'field_product_supplierinfo__x_vendor_lead_days',
         [('model', '=', 'product.supplierinfo'), ('name', '=', 'x_vendor_lead_days')]),
        ('ir.model.fields', 'field_product_supplierinfo__x_transit_min',
         [('model', '=', 'product.supplierinfo'), ('name', '=', 'x_transit_min')]),
        ('ir.model.fields', 'field_product_supplierinfo__x_transit_max',
         [('model', '=', 'product.supplierinfo'), ('name', '=', 'x_transit_max')]),
        ('ir.model.fields', 'field_product_supplierinfo__x_offer_source',
         [('model', '=', 'product.supplierinfo'), ('name', '=', 'x_offer_source')]),
        ('ir.model.fields', 'field_product_supplierinfo__x_lead_total',
         [('model', '=', 'product.supplierinfo'), ('name', '=', 'x_lead_total')]),
    ]

    for model_name, xml_id, domain in EXTERNAL_ID_MAP:
        existing = IrModelData.search([
            ('module', '=', module),
            ('name', '=', xml_id),
        ], limit=1)
        if existing:
            skipped += 1
            continue

        target_record = env[model_name].search(domain, limit=1)
        if not target_record:
            _logger.warning(
                'networkser_broker: record not found for %s: %s',
                xml_id, domain,
            )
            not_found += 1
            continue

        IrModelData.create({
            'module': module,
            'name': xml_id,
            'model': model_name,
            'res_id': target_record.id,
        })
        created += 1

    _logger.info(
        'networkser_broker Phase 1 (fields + model): '
        'created=%d skipped=%d not_found=%d',
        created, skipped, not_found,
    )

    # ── Phase 2: Delete old DB-only views superseded by module views ──
    # These views had DB IDs 9404-9409 + 9300 before the module was installed.
    # The module XML creates equivalent views with proper external IDs.
    # The old DB-only views are now orphans and must be removed.
    View = env['ir.ui.view']
    removed_views = 0
    kept_views = 0

    OLD_VIEW_SIGNATURES = [
        ('product.template', 'product.template.form.broker.channels'),
        ('product.template', 'product.template.form.brand.mpn (NET-1506)'),
        ('product.supplierinfo', 'product.supplierinfo.list.broker.lead.1070'),
        ('product.supplierinfo', 'product.supplierinfo.list.broker.lead.481'),
        ('product.supplierinfo', 'product.supplierinfo.offer.source.9405'),
        ('product.supplierinfo', 'product.supplierinfo.offer.source.9406'),
        ('product.supplierinfo', 'product.supplierinfo.lead.total'),
    ]

    for model_name, view_name in OLD_VIEW_SIGNATURES:
        # Find the module-backed view (has an external ID in our module)
        module_view_xml_ids = IrModelData.search([
            ('module', '=', module),
            ('model', '=', 'ir.ui.view'),
        ])
        module_view_ids = module_view_xml_ids.mapped('res_id')

        # Find ALL views with this name+model
        all_named = View.search([
            ('model', '=', model_name),
            ('name', '=', view_name),
        ])

        module_views = all_named.filtered(lambda v: v.id in module_view_ids)
        orphan_views = all_named.filtered(lambda v: v.id not in module_view_ids)

        if module_views and orphan_views:
            # Module version exists → delete old DB-only orphans
            _logger.info(
                'networkser_broker: removing %d orphan view(s) '
                'for %s (module version exists)',
                len(orphan_views), view_name,
            )
            orphan_views.unlink()
            removed_views += len(orphan_views)
            kept_views += len(module_views)
        elif module_views and not orphan_views:
            # Already clean
            kept_views += len(module_views)
        elif not module_views and orphan_views:
            # No module view (shouldn't happen on proper install)
            _logger.warning(
                'networkser_broker: orphan views for %s but no module '
                'version found — keeping orphans', view_name,
            )
            kept_views += len(orphan_views)

    _logger.info(
        'networkser_broker Phase 2 (view cleanup): '
        'removed=%d kept=%d',
        removed_views, kept_views,
    )