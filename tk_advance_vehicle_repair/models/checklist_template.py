# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class CheckListTemplateItems(models.Model):
    """Check List Template Items"""
    _name = 'checklist.template.item'
    _description = __doc__
    _order = "sequence"
    _rec_name = 'name'

    sequence = fields.Integer(default=0)
    name = fields.Char(string="Title", required=True)
    display_type = fields.Selection(selection=[
        ('line_section', "Section"),
        ('line_note', "Note")],
        default=False)
    checklist_template_id = fields.Many2one('checklist.template')


class ChecklistTemplate(models.Model):
    """Check List Template"""
    _name = 'checklist.template'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(required=True, translate=True)
    checklist_template_item_ids = fields.One2many(comodel_name='checklist.template.item',
                                                  inverse_name='checklist_template_id',
                                                  string="Checklist Items")

    @api.constrains('checklist_template_item_ids')
    def _check_template_name(self):
        """Check template name"""
        for record in self:
            if not record.checklist_template_item_ids:
                raise ValidationError(_("The Title field cannot be empty."))


class InspectionChecklist(models.Model):
    """Inspection Check list"""
    _name = 'inspection.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _order = "sequence"
    _rec_name = 'name'

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)
    description = fields.Char(translate=True)
    display_type = fields.Selection(selection=[
        ('line_section', "Section"),
        ('line_note', "Note")],
        default=False)
    is_check = fields.Boolean(string="Check")
    inspection_job_card_id = fields.Many2one('inspection.job.card')


class RepairChecklist(models.Model):
    """Repair Check list"""
    _name = 'repair.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _order = "sequence"
    _rec_name = 'name'

    sequence = fields.Integer()
    name = fields.Char(required=True, translate=True)
    description = fields.Char(translate=True)
    display_type = fields.Selection(selection=[
        ('line_section', "Section"),
        ('line_note', "Note")],
        default=False)
    is_check = fields.Boolean(string="Check")
    repair_job_card_id = fields.Many2one('repair.job.card')
