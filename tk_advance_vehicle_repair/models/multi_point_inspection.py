# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehicleComponent(models.Model):
    """Vehicle Component"""
    _name = "vehicle.component"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(translate=True)
    compo_vehicle_side = fields.Selection([
        ('top_side', "Top Side"),
        ('bottom_side', "Bottom Side")],
        string="Vehicle Side")

    @api.constrains('compo_vehicle_side')
    def _check_compo_vehicle_side(self):
        """Check Compo Vehicle Side"""
        for record in self:
            if not record.compo_vehicle_side:
                raise ValidationError(_("Please select a vehicle side: Top Side or Bottom Side"))


class VehicleFluid(models.Model):
    """Vehicle Fluid"""
    _name = "vehicle.fluid"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(translate=True)
    fluid_vehicle_side = fields.Selection([
        ('top_side', "Top Side"),
        ('bottom_side', "Bottom Side")],
        string="Vehicle Side")

    @api.constrains('fluid_vehicle_side')
    def _check_fluid_vehicle_side(self):
        """Check Fluid Vehicle Side"""
        for record in self:
            if not record.fluid_vehicle_side:
                raise ValidationError(_("Please select a vehicle side: Top Side or Bottom Side"))


class VehicleComponents(models.Model):
    """Vehicle Components"""
    _name = "vehicle.components"
    _description = __doc__
    _rec_name = 'vehicle_component_id'

    avatar = fields.Binary(string="Image")
    vehicle_component_id = fields.Many2one('vehicle.component', string="Component", required=True,
                                           domain="[('compo_vehicle_side', '=', c_vehicle_side)]")
    c_vehicle_side = fields.Selection([
        ('top_side', "Top Side"),
        ('bottom_side', "Bottom Side")],
        string="Vehicle Side", required=True)
    condition = fields.Selection([
        ('require_future_attention', "Require Future Attention"),
        ('require_immediate_attention', "Require Immediate Attention"),
        ('checked_ok', "Checked and Okay at this Time")],
        string="Present Condition")
    remarks = fields.Char(translate=True, size=50)
    inspection_job_card_id = fields.Many2one('inspection.job.card')


class VehicleFluids(models.Model):
    """Vehicle Fluids"""
    _name = "vehicle.fluids"
    _description = __doc__
    _rec_name = 'vehicle_fluid_id'

    avatar = fields.Binary(string="Image")
    vehicle_fluid_id = fields.Many2one('vehicle.fluid', string="Fluid", required=True,
                                       domain="[('fluid_vehicle_side', '=', f_vehicle_side)]")
    f_vehicle_side = fields.Selection([
        ('top_side', "Top Side"),
        ('bottom_side', "Bottom Side")],
        string="Vehicle Side", required=True)
    condition = fields.Selection([
        ('require_future_attention', "Require Future Attention"),
        ('require_immediate_attention', "Require Immediate Attention"),
        ('checked_ok', "Checked and Okay at this Time")],
        string="Present Condition")
    remarks = fields.Char(translate=True, size=50)
    inspection_job_card_id = fields.Many2one('inspection.job.card')


class TyreInspection(models.Model):
    """Tire Inspection"""
    _name = 'tyre.inspection'
    _description = __doc__
    _rec_name = 'tyre'

    avatar = fields.Binary(string="Image")
    tyre = fields.Selection([
        ('lf', "Left Front"),
        ('rf', "Right Front"),
        ('lr', "Left Rear"),
        ('rr', "Right Rear")],
        string="Tire Location", required=True)
    tread_wear = fields.Char(translate=True)
    tread_depth = fields.Char(translate=True)
    tyre_pressure = fields.Char(string="Tire Pressure", translate=True)
    brake_pads = fields.Float(string="Brake pads (%)")
    condition = fields.Selection([
        ('require_future_attention', "Require Future Attention"),
        ('require_immediate_attention', "Require Immediate Attention"),
        ('checked_ok', "Checked and Okay at this Time")],
        string="Present Condition")
    inspection_job_card_id = fields.Many2one('inspection.job.card')
