# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehicleConditionLocation(models.Model):
    """Vehicle Condition Location"""
    _name = "vehicle.condition.location"
    _description = __doc__
    _rec_name = 'location'

    location = fields.Char(required=True, translate=True)


class VehicleCondition(models.Model):
    """Vehicle Condition"""
    _name = "vehicle.condition"
    _description = __doc__
    _rec_name = 'condition'

    condition = fields.Char(required=True, translate=True)
    condition_code = fields.Char(translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Check if a Condition Code already exists before creating a new record."""
        for vals in vals_list:
            condition_code = vals.get('condition_code')
            if condition_code:
                existing_record = self.search([('condition_code', '=', condition_code)], limit=1)
                if existing_record:
                    raise ValidationError(_(
                        "Condition Code %s is already in use. Please try a different one.",
                        condition_code))
        return super().create(vals_list)

    def write(self, vals):
        """Check if a Condition Code already exists before updating a record."""
        if 'condition_code' in vals:
            new_condition_code = vals['condition_code']
            if new_condition_code:
                for record in self:
                    existing_record = self.search(
                        [('condition_code', '=', new_condition_code), ('id', '!=', record.id)],
                        limit=1)
                    if existing_record:
                        raise ValidationError(_(
                            "Condition Code %s is already in use. Please try a different one.",
                            new_condition_code))
        return super().write(vals)


class VehicleConditionLine(models.Model):
    """Vehicle Condition Line"""
    _name = "vehicle.condition.line"
    _description = __doc__
    _rec_name = 'vehicle_view'

    avatar = fields.Binary(string="Image")
    vehicle_view = fields.Selection([
        ('top', "Top View"),
        ('bottom', "Bottom View"),
        ('left_side', "Left Side View"),
        ('right_side', "Right Side View"),
        ('front', "Front View"),
        ('back', "Back View")])
    vehicle_condition_location_id = fields.Many2one('vehicle.condition.location', string="Location")
    vehicle_condition_id = fields.Many2one('vehicle.condition', string="Condition")
    condition_code = fields.Char(translate=True)
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete="cascade")

    @api.onchange('vehicle_condition_id')
    def _onchange_vehicle_condition_code(self):
        """Onchange Condition Code"""
        for rec in self:
            rec.condition_code = rec.vehicle_condition_id.condition_code


class VehicleItem(models.Model):
    """Vehicle Item"""
    _name = "vehicle.item"
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(translate=True)
    item_category = fields.Selection([
        ('mechanical', "Mechanical Item"),
        ('interior', "Interior Item")],
        string="Category")

    @api.constrains('item_category')
    def _check_item_category(self):
        """Check Item Category"""
        for record in self:
            if not record.item_category:
                raise ValidationError(
                    _("Please select a category type: Mechanical Item or Interior Item"))


class MechanicalItemCondition(models.Model):
    """Mechanical Item Condition"""
    _name = "mechanical.item.condition"
    _description = __doc__
    _rec_name = 'vehicle_item_id'

    avatar = fields.Binary(string="Image")
    vehicle_item_id = fields.Many2one('vehicle.item', string="Name", required=True,
                                      domain="[('item_category', '=', 'mechanical')]")
    mechanical_condition = fields.Selection([
        ('poor', "Poor"),
        ('average', "Average"),
        ('not_working', "Not Working"),
        ('good', "Good"),
        ('other', "Other")],
        string="Condition")
    mechanical_condition_notes = fields.Char(string="Remarks", translate=True, size=50)
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete="cascade")


class InteriorItemCondition(models.Model):
    """Interior Item Condition"""
    _name = "interior.item.condition"
    _description = __doc__
    _rec_name = 'vehicle_item_id'

    avatar = fields.Binary(string="Image")
    vehicle_item_id = fields.Many2one('vehicle.item', string="Name", required=True,
                                      domain="[('item_category', '=', 'interior')]")
    interior_condition = fields.Selection([
        ('worn', "Worn"),
        ('burnt', "Burnt"),
        ('ripped', "Ripped"),
        ('good', "Good"),
        ('other', "Other")],
        string="Condition")
    interior_condition_notes = fields.Char(string="Remarks", translate=True, size=50)
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete="cascade")
