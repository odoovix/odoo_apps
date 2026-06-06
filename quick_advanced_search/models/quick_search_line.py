# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QuickSearchLine(models.Model):
    _name = 'quick.search.line'
    _description = 'Quick Search Field'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    config_id = fields.Many2one(
        'quick.search.config',
        string='Configuration',
        required=True,
        ondelete='cascade',
    )
    model_id = fields.Many2one(related='config_id.model_id', store=True, readonly=True)
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Field',
        required=True,
        ondelete='cascade',
        domain="[('model_id', '=', model_id), ('store', '=', True), ('ttype', 'not in', ['binary', 'one2many', 'many2many', 'reference', 'properties'])]",
    )
    label = fields.Char(required=True)
    field_name = fields.Char(related='field_id.name', store=True, readonly=True, string='Field Name')
    field_type = fields.Selection(related='field_id.ttype', store=True, readonly=True, string='Field Type')
    operator = fields.Selection([
        ('contains', 'contains'),
        ('not_contains', 'does not contain'),
        ('equal', 'is equal to'),
        ('not_equal', 'is not equal to'),
        ('starts_with', 'starts with'),
        ('ends_with', 'ends with'),
        ('greater', 'is greater than'),
        ('less', 'is less than'),
        ('between', 'is between'),
    ], default='contains', required=True)

    @api.onchange('field_id')
    def _onchange_field_id(self):
        for line in self:
            if line.field_id:
                line.label = line.field_id.field_description or line.field_id.name
                line.operator = line._default_operator_for_type(line.field_id.ttype)

    @api.constrains('field_id', 'config_id')
    def _check_field_model(self):
        for line in self:
            if line.field_id and line.config_id and line.field_id.model_id != line.config_id.model_id:
                raise ValidationError(_('The selected field must belong to the configured model.'))

    @api.model
    def _default_operator_for_type(self, field_type):
        if field_type in ('integer', 'float', 'monetary', 'date', 'datetime'):
            return 'equal'
        if field_type == 'boolean':
            return 'equal'
        return 'contains'

    def _domain_for_term(self, term):
        self.ensure_one()
        field_name = self.field_name
        field_type = self.field_type
        if not field_name or not term:
            return []

        if field_type in ('char', 'text', 'html', 'many2one', 'selection'):
            return self._text_domain(field_name, term)
        if field_type == 'boolean':
            return self._boolean_domain(field_name, term)
        if field_type in ('integer', 'float', 'monetary'):
            return self._number_domain(field_name, term)
        if field_type in ('date', 'datetime'):
            return self._date_domain(field_name, term, field_type)
        return []

    def _text_domain(self, field_name, term):
        if self.operator == 'not_contains':
            return [(field_name, 'not ilike', term)]
        if self.operator == 'equal':
            return [(field_name, '=', term)]
        if self.operator == 'not_equal':
            return [(field_name, '!=', term)]
        if self.operator == 'starts_with':
            return [(field_name, '=ilike', '%s%%' % term)]
        if self.operator == 'ends_with':
            return [(field_name, '=ilike', '%%%s' % term)]
        return [(field_name, 'ilike', term)]

    def _boolean_domain(self, field_name, term):
        normalized = term.strip().lower()
        if normalized in ('true', 'yes', 'y', '1', 'active'):
            value = True
        elif normalized in ('false', 'no', 'n', '0', 'inactive'):
            value = False
        else:
            return []
        operator = '!=' if self.operator == 'not_equal' else '='
        return [(field_name, operator, value)]

    def _number_domain(self, field_name, term):
        if self.operator == 'between':
            values = self._parse_number_values(term)
            if len(values) < 2:
                return []
            return [(field_name, '>=', values[0]), (field_name, '<=', values[1])]
        try:
            value = float(term.strip())
        except (TypeError, ValueError):
            return []
        if self.field_type == 'integer':
            if not value.is_integer():
                return []
            value = int(value)
        operator = {
            'greater': '>',
            'less': '<',
            'not_equal': '!=',
        }.get(self.operator, '=')
        return [(field_name, operator, value)]

    def _parse_number_values(self, term):
        clean_term = (term or '').strip()
        separators = ['..', ' to ', ' - ']
        chunks = [clean_term]
        for separator in separators:
            if separator in clean_term:
                chunks = [chunk.strip() for chunk in clean_term.split(separator, 1)]
                break
        values = []
        for chunk in chunks:
            try:
                value = float(chunk)
            except (TypeError, ValueError):
                return []
            if self.field_type == 'integer':
                if not value.is_integer():
                    return []
                value = int(value)
            values.append(value)
        return values

    def _date_domain(self, field_name, term, field_type):
        values = self._parse_date_values(term)
        if not values:
            return []
        if self.operator == 'between' and len(values) >= 2:
            start, end = values[0], values[1]
            return [(field_name, '>=', self._format_date_value(start, field_type, False)),
                    (field_name, '<=', self._format_date_value(end, field_type, True))]
        if field_type == 'datetime' and self.operator == 'equal':
            value = values[0]
            return [(field_name, '>=', self._format_date_value(value, field_type, False)),
                    (field_name, '<=', self._format_date_value(value, field_type, True))]
        value = self._format_date_value(values[0], field_type, False)
        operator = {
            'greater': '>',
            'less': '<',
            'not_equal': '!=',
        }.get(self.operator, '=')
        return [(field_name, operator, value)]

    def _parse_date_values(self, term):
        clean_term = (term or '').strip()
        separators = ['..', ' to ', ' - ']
        chunks = [clean_term]
        for separator in separators:
            if separator in clean_term:
                chunks = [chunk.strip() for chunk in clean_term.split(separator, 1)]
                break
        values = []
        for chunk in chunks:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                try:
                    values.append(datetime.strptime(chunk, fmt).date())
                    break
                except ValueError:
                    continue
        return values

    def _format_date_value(self, value, field_type, end_of_day):
        if field_type == 'datetime':
            dt_value = datetime.combine(value, time.max if end_of_day else time.min)
            return fields.Datetime.to_string(dt_value)
        return fields.Date.to_string(value)
