# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class UniversalExportRelLine(models.Model):
    """
    One row = one column in the export output, sourced from the *sub-model*
    (e.g. Sales Order Line).
    """
    _name = 'universal.export.rel.line'
    _description = 'Universal Export Related Field'
    _order = 'sequence, id'

    export_id = fields.Many2one(
        'universal.export.rule', string='Export Rule',
        required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)

    field_id = fields.Many2one(
        'ir.model.fields', string='Name', required=True,
        domain="[('model_id', '=', parent.sub_model_id)]",
        ondelete='cascade',
    )

    model_id_rel = fields.Many2one(
        'ir.model', string='Model',
        compute='_compute_model_id_rel', store=True, readonly=True,
    )

    rel_field_id = fields.Many2one(
        'ir.model.fields', string='Relation Field',
        domain="[('model_id', '=', model_id_rel)]",
        ondelete='set null',
    )

    label = fields.Char(
        string='Label',
        compute='_compute_label', store=True, readonly=False,
        help='Column header in the exported file. Defaults to the field description.',
    )

    @api.depends('field_id')
    def _compute_model_id_rel(self):
        IrModel = self.env['ir.model']
        for line in self:
            rel = line.field_id.relation if line.field_id else False
            if rel:
                line.model_id_rel = IrModel.search([('model', '=', rel)], limit=1)
            else:
                line.model_id_rel = False

    @api.depends('field_id')
    def _compute_label(self):
        for line in self:
            if line.field_id and not line.label:
                line.label = line.field_id.field_description

    @api.onchange('field_id')
    def _onchange_field_id(self):
        self.rel_field_id = False
        if self.field_id:
            self.label = self.field_id.field_description

    @api.constrains('export_id', 'field_id', 'rel_field_id')
    def _check_field_configuration(self):
        for line in self:
            sub_model = (
                line.export_id.sub_model_id
                or line.export_id._get_sub_model_from_rel_field(line.export_id.rel_field_id)
            )
            if not sub_model:
                raise ValidationError(_('Related export fields require a sub model on the export rule.'))
            if line.field_id and line.field_id.model_id != sub_model:
                raise ValidationError(_(
                    'The related field "%(field)s" must belong to the sub model "%(model)s".',
                    field=line.field_id.name,
                    model=sub_model.model,
                ))
            if line.rel_field_id:
                relation = line.field_id.relation
                if not relation:
                    raise ValidationError(_(
                        'A relation field can only be set when "%s" is a relational field.',
                        line.field_id.name,
                    ))
                if line.rel_field_id.model_id.model != relation:
                    raise ValidationError(_(
                        'The relation field "%(rel_field)s" must belong to "%(relation)s".',
                        rel_field=line.rel_field_id.name,
                        relation=relation,
                    ))
