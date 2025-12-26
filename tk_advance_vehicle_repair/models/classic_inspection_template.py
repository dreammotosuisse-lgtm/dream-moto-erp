# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ClassicInspectionTemplate(models.Model):
    """Classic Inspection Template"""
    _name = 'classic.inspection.template'
    _description = __doc__

    name = fields.Char(string='Title', translate=True)

    inspection_report_type = fields.Selection(
        [('advanced_inspection', "Advanced Inspection"),
         ('classic_inspection', "Classic Inspection")],
        string="Inspection Type", default='advanced_inspection')

    # Classic Inspection
    exterior_part = fields.Boolean()
    interior_part = fields.Boolean()
    under_hood_part = fields.Boolean()
    under_vehicle_part = fields.Boolean()
    is_fluid = fields.Boolean(string="Vehicle Fluid")
    is_tire_condition = fields.Boolean(string="Tire Condition")
    is_brake_condition = fields.Boolean(string="Brake Condition")

    # Advanced Inspection
    is_interior_item = fields.Boolean(string="Interior")
    is_exterior_item = fields.Boolean(string="Exterior")
    is_mechanical_item = fields.Boolean(string="Mechanical")
    is_vehicle_component = fields.Boolean(string="Component")
    is_vehicle_fluid = fields.Boolean(string="Fluid")

    # Classic Inspection
    classic_exterior_part_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                 relation='temp_exterior_part_rel',
                                                 column1='template_id',
                                                 column2='temp_exterior_part_id',
                                                 domain=[('type', '=', 'exterior')])

    classic_interior_part_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                 relation='temp_interior_part_rel',
                                                 column1='template_id',
                                                 column2='temp_interior_part_id',
                                                 domain=[('type', '=', 'interior')])

    classic_under_hood_part_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                   relation='temp_under_hood_part_rel',
                                                   column1='template_id',
                                                   column2='temp_under_hood_part_id',
                                                   domain=[('type', '=', 'under_hood')])

    classic_under_vehicle_part_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                      relation='temp_under_vehicle_part_rel',
                                                      column1='template_id',
                                                      column2='temp_under_vehicle_part_id',
                                                      domain=[('type', '=', 'under_vehicle')])

    classic_fluid_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                         relation='temp_fluids_rel',
                                         column1='template_id',
                                         column2='temp_fluids_id',
                                         domain=[('type', '=', 'fluids')])

    classic_tire_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                        relation='temp_tires_rel',
                                        column1='template_id',
                                        column2='temp_tires_id',
                                        domain=[('type', '=', 'tires')])

    classic_brake_condition_ids = fields.Many2many(comodel_name='vehicle.part.info',
                                                   relation='temp_brake_condition_rel',
                                                   column1='template_id',
                                                   column2='temp_brake_condition_id',
                                                   domain=[('type', '=', 'brake_condition')])

    # Advanced Inspection
    advance_interior_item_ids = fields.Many2many(comodel_name='vehicle.item',
                                                 relation='temp_interior_item_rel',
                                                 column1='interior_template_id',
                                                 column2='temp_interior_item_id',
                                                 domain=[('item_category', '=', 'interior')])

    advance_exterior_item_ids = fields.One2many(comodel_name='advance.exterior.item',
                                                inverse_name='classic_inspection_template_id')

    advance_mechanical_item_ids = fields.Many2many(comodel_name='vehicle.item',
                                                   relation='temp_mechanical_item_rel',
                                                   column1='mechanical_template_id',
                                                   column2='temp_mechanical_item_id',
                                                   domain=[('item_category', '=', 'mechanical')])

    advance_vehicle_component_ids = fields.Many2many(comodel_name='vehicle.component',
                                                     relation='temp_vehicle_compo_rel',
                                                     column1='component_template_id',
                                                     column2='vehicle_advance_compo_id')

    advance_vehicle_fluid_ids = fields.Many2many(comodel_name='vehicle.fluid',
                                                 relation='temp_vehicle_fluid_rel',
                                                 column1='fluid_template_id',
                                                 column2='vehicle_advance_fluid_id')

    @api.constrains(
        'inspection_report_type',
        'is_exterior_item', 'is_interior_item', 'is_mechanical_item',
        'is_vehicle_component', 'is_vehicle_fluid',
        'exterior_part', 'interior_part', 'under_hood_part', 'under_vehicle_part',
        'is_fluid', 'is_tire_condition', 'is_brake_condition'
    )
    def _check_inspection_booleans(self):
        """Ensure at least one section is selected for inspection."""
        for record in self:
            if record.inspection_report_type == 'advanced_inspection':
                if not any([
                    record.is_exterior_item,
                    record.is_interior_item,
                    record.is_mechanical_item,
                    record.is_vehicle_component,
                    record.is_vehicle_fluid,
                ]):
                    raise ValidationError(_("Please select at least one inspection category."))
            elif record.inspection_report_type == 'classic_inspection':
                if not any([
                    record.exterior_part,
                    record.interior_part,
                    record.under_hood_part,
                    record.under_vehicle_part,
                    record.is_fluid,
                    record.is_tire_condition,
                    record.is_brake_condition,
                ]):
                    raise ValidationError(_("Please select at least one inspection category."))

    @api.constrains('inspection_report_type', 'is_exterior_item', 'is_interior_item',
                    'is_mechanical_item', 'is_vehicle_component', 'is_vehicle_fluid',
                    'exterior_part', 'interior_part', 'under_hood_part', 'under_vehicle_part',
                    'is_fluid', 'is_tire_condition', 'is_brake_condition')
    def _check_inspection_items_templates(self):
        """Ensure at least one value is added when boolean are selected."""
        for record in self:
            if record.inspection_report_type == 'advanced_inspection':
                if record.is_exterior_item and not record.advance_exterior_item_ids:
                    raise ValidationError(
                        _("Please add at least one exterior items when Exterior is selected."))
                if record.is_interior_item and not record.advance_interior_item_ids:
                    raise ValidationError(
                        _("Please add at least one interior items when Interior is selected."))
                if record.is_mechanical_item and not record.advance_mechanical_item_ids:
                    raise ValidationError(
                        _("Please add at least one mechanical items when Mechanical is selected."))
                if record.is_vehicle_component and not record.advance_vehicle_component_ids:
                    raise ValidationError(
                        _("Please add at least one vehicle components when Component is selected."))
                if record.is_vehicle_fluid and not record.advance_vehicle_fluid_ids:
                    raise ValidationError(
                        _("Please add at least one vehicle fluids when Fluid is selected."))
            if record.inspection_report_type == 'classic_inspection':
                if record.exterior_part and not record.classic_exterior_part_ids:
                    raise ValidationError(
                        _("Please add at least one exterior parts when Exterior Part is selected."))
                if record.interior_part and not record.classic_interior_part_ids:
                    raise ValidationError(
                        _("Please add at least one interior parts when Interior Part is selected."))
                if record.under_hood_part and not record.classic_under_hood_part_ids:
                    raise ValidationError(
                        _("Please add at least one under hood parts when Under Hood Part is selected."))
                if record.under_vehicle_part and not record.classic_under_vehicle_part_ids:
                    raise ValidationError(
                        _("Please add at least one under vehicle parts when Under Vehicle Part is selected."))
                if record.is_fluid and not record.classic_fluid_ids:
                    raise ValidationError(
                        _("Please add at least one vehicle fluids when Vehicle Fluid is selected."))
                if record.is_tire_condition and not record.classic_tire_ids:
                    raise ValidationError(
                        _("Please add at least one tire conditions when Tire Condition is selected."))
                if record.is_brake_condition and not record.classic_brake_condition_ids:
                    raise ValidationError(
                        _("Please add at least one brake conditions when Brake Condition is selected."))


class AdvanceExteriorItem(models.Model):
    """Advance Exterior Item"""
    _name = "advance.exterior.item"
    _description = __doc__
    _rec_name = 'vehicle_view'

    vehicle_view = fields.Selection([
        ('top', "Top View"),
        ('bottom', "Bottom View"),
        ('left_side', "Left Side View"),
        ('right_side', "Right Side View"),
        ('front', "Front View"),
        ('back', "Back View")])
    vehicle_condition_location_id = fields.Many2one('vehicle.condition.location', string="Location")
    classic_inspection_template_id = fields.Many2one('classic.inspection.template',
                                                     ondelete='cascade')
