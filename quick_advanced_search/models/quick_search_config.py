# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class QuickSearchConfig(models.Model):
    _name = 'quick.search.config'
    _description = 'Quick Search Configuration'
    _rec_name = 'model_id'
    _order = 'model_id'

    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        domain=[('transient', '=', False)],
        help='Model where this quick search configuration is applied.',
    )
    model_name = fields.Char(related='model_id.model', store=True, string='Model Technical Name')
    active = fields.Boolean(default=True)
    line_ids = fields.One2many(
        'quick.search.line',
        'config_id',
        string='Search Fields',
        copy=True,
    )

    _sql_constraints = [
        (
            'quick_search_model_unique',
            'unique(model_id)',
            'Only one quick search configuration is allowed per model.',
        ),
    ]

    @api.constrains('line_ids')
    def _check_has_lines(self):
        for config in self:
            if config.active and not config.line_ids:
                raise ValidationError(_('Add at least one search field or archive the configuration.'))

    @api.model
    def _expand_domain_for_model(self, model_name, domain):
        if not domain or not model_name:
            return domain or []

        terms = self._extract_simple_text_terms(domain)
        if not terms:
            return domain

        config = self.with_context(quick_search_skip_expand=True).search([
            ('model_name', '=', model_name),
            ('active', '=', True),
        ], limit=1)
        if not config or not config.line_ids:
            return domain

        expanded_parts = [domain]
        for term in terms:
            quick_domain = config._build_term_domain(term)
            if quick_domain:
                expanded_parts.append(quick_domain)
        return expression.OR(expanded_parts) if len(expanded_parts) > 1 else domain

    @api.model
    def _extract_simple_text_terms(self, domain):
        leaves = [item for item in domain if isinstance(item, (tuple, list)) and len(item) == 3]
        if not leaves:
            return []
        terms = []
        for field_name, operator, value in leaves:
            if operator in ('ilike', '=ilike') and isinstance(value, str):
                terms.append(value.strip())
        return list(dict.fromkeys(term for term in terms if term))

    def _build_term_domain(self, term):
        self.ensure_one()
        parts = []
        for line in self.line_ids.filtered('active'):
            leaf_domain = line._domain_for_term(term)
            if leaf_domain:
                parts.append(leaf_domain)
        return expression.OR(parts) if parts else []
