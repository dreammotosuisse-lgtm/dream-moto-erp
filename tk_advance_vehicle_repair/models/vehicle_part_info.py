# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehiclePartInfo(models.Model):
    """Vehicle Part Info"""
    _name = "vehicle.part.info"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(required=True)
    type = fields.Selection([
        ('exterior', "Exterior"),
        ('interior', "Interior"),
        ('under_hood', "Under Hood"),
        ('under_vehicle', "Under Vehicle"),
        ('fluids', "Fluids"),
        ('tires', "Tires"),
        ('brake_condition', "Brake Condition")])

    @api.constrains('type')
    def _constrain_check_part_type(self):
        """Check Part type """
        for record in self:
            if not record.type:
                raise ValidationError(_("Please select a any one type of part"))


class ExteriorVehiclePart(models.Model):
    """Exterior Vehicle Part"""
    _name = "exterior.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'exterior')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        """ Onchange okay for now """
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        """ Onchange further attention """
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        """ Onchange required attention """
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        """ Onchange nor inspected """
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return


class InteriorVehiclePart(models.Model):
    """Interior Vehicle Part"""
    _name = "interior.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'interior')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return


class UnderHoodVehiclePart(models.Model):
    """Under Hood Vehicle Part"""
    _name = "under.hood.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'under_hood')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return


class UnderVehiclePart(models.Model):
    """Under Vehicle Part"""
    _name = "under.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'under_vehicle')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return


class FluidsVehiclePart(models.Model):
    """Fluids Vehicle Part"""
    _name = "fluids.vehicle.part"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Part", domain=[('type', '=', 'fluids')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()
    filled = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False
            self.filled = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False
            self.filled = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False
            self.filled = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False
            self.filled = False

    @api.onchange('filled')
    def _onchange_filled(self):
        if self.filled:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return


class VehiclePartTires(models.Model):
    """Vehicle Part Tires"""
    _name = "vehicle.part.tires"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info',
                                           string="Tire Pressure", domain=[('type', '=', 'tires')])
    incoming = fields.Char()
    adjusted_to = fields.Char(string="Adjusted to")
    tread_depth = fields.Char()
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return


class VehicleBrakeCondition(models.Model):
    """Vehicle Brake Condition"""
    _name = "vehicle.brake.condition"
    _description = __doc__
    _rec_name = 'vehicle_part_info_id'

    avatar = fields.Binary()
    vehicle_part_info_id = fields.Many2one('vehicle.part.info', string="Part",
                                           domain=[('type', '=', 'brake_condition')])
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')

    okay_for_now = fields.Boolean()
    further_attention = fields.Boolean()
    required_attention = fields.Boolean()
    not_inspected = fields.Boolean()

    @api.onchange('okay_for_now')
    def _onchange_okay_for_now(self):
        if self.okay_for_now:
            self.further_attention = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('further_attention')
    def _onchange_further_attention(self):
        if self.further_attention:
            self.okay_for_now = False
            self.required_attention = False
            self.not_inspected = False

    @api.onchange('required_attention')
    def _onchange_required_attention(self):
        if self.required_attention:
            self.further_attention = False
            self.okay_for_now = False
            self.not_inspected = False

    @api.onchange('not_inspected')
    def _onchange_not_inspected(self):
        if self.not_inspected:
            self.required_attention = False
            self.further_attention = False
            self.okay_for_now = False

    def action_inspection_button(self):
        """ Action Inspection Button """
        return
