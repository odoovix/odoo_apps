# -*- coding: utf-8 -*-

from odoo import api, models
from lxml import etree


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type != 'search' or self.env.context.get('quick_search_skip_expand'):
            return result

        config = self.env['quick.search.config'].sudo().with_context(
            quick_search_skip_expand=True
        ).search([
            ('model_name', '=', self._name),
            ('active', '=', True),
        ], limit=1)
        if not config or not config.line_ids:
            return result

        root = etree.fromstring(result['arch'])
        existing_fields = set(root.xpath('//field/@name'))
        for line in config.line_ids.filtered('active'):
            if not line.field_name or line.field_name in existing_fields:
                continue
            field_node = etree.Element('field', name=line.field_name)
            if line.label:
                field_node.set('string', line.label)
            root.insert(0, field_node)
            existing_fields.add(line.field_name)
        result['arch'] = etree.tostring(root, encoding='unicode')
        return result

    @api.model
    @api.readonly
    def web_search_read(self, domain=None, *args, **kwargs):
        if not self.env.context.get('quick_search_skip_expand'):
            domain = self.env['quick.search.config'].sudo()._expand_domain_for_model(
                self._name, domain or []
            )
        return super().web_search_read(domain, *args, **kwargs)
