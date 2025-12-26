# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class RegisterVehicle(models.Model):
    """Register Vehicle"""
    _name = 'register.vehicle'
    _description = __doc__
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    registration_no = fields.Char(string="Registration No.")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    transmission_type = fields.Selection([
        ('manual', "Manual"),
        ('automatic', "Automatic"),
        ('cvt', "CVT")])
    vin_no = fields.Char(string="VIN Number")

    make = fields.Char(string="Make")
    manufacturing_year = fields.Char(string="Year")
    service_history_ids = fields.One2many(comodel_name='service.history',
                                          inverse_name='register_vehicle_id')

    inspection_job_card_count = fields.Integer(compute='_compute_inspection_job_card_count')
    repair_job_card_count = fields.Integer(compute='_compute_repair_job_card_count')
    vehicle_booking_count = fields.Integer(compute='_compute_vehicle_booking_count')

    @api.model_create_multi
    def create(self, vals_list):
        """Check if a registration number already exists before creating a new record."""
        for vals in vals_list:
            registration_no = vals.get('registration_no')
            if registration_no:
                existing_record = self.search([('registration_no', '=', registration_no)], limit=1)
                if existing_record:
                    raise ValidationError(_(
                        "Registration %s is already in use. Please try a different one.",
                        registration_no))
        return super().create(vals_list)

    @api.depends('vehicle_brand_id', 'vehicle_model_id', 'registration_no')
    def _compute_display_name(self):
        for rec in self:
            brand_name = rec.vehicle_brand_id.name or ''
            model_name = rec.vehicle_model_id.name or ''
            registration_no = rec.registration_no or ''
            rec.display_name = f"{brand_name}/{model_name}/{registration_no}"

    @api.onchange('vehicle_brand_id')
    def _onchange_register_vehicle_brand(self):
        """Onchange vehicle brand"""
        for rec in self:
            rec.vehicle_model_id = False

    def _compute_inspection_job_card_count(self):
        """Compute Inspection JobCard Count"""
        for rec in self:
            rec.inspection_job_card_count = self.env['inspection.job.card'].search_count(
                [('register_vehicle_id', '=', rec.id)])

    def action_view_inspection_job_cards(self):
        """Views Inspection JobCards"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection JobCards'),
            'res_model': 'inspection.job.card',
            'domain': [('register_vehicle_id', '=', self.id)],
            'context': {
                'create': False
            },
            'view_mode': 'kanban,list,form,pivot,search,activity',
            'target': 'current'
        }

    def _compute_repair_job_card_count(self):
        """Compute Repair JobCard Count"""
        for rec in self:
            rec.repair_job_card_count = self.env['repair.job.card'].search_count(
                [('register_vehicle_id', '=', rec.id)])

    def action_view_repair_job_cards(self):
        """Views Repair JobCards"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair JobCards'),
            'res_model': 'repair.job.card',
            'domain': [('register_vehicle_id', '=', self.id)],
            'context': {
                'create': False
            },
            'view_mode': 'kanban,list,form,pivot,search,activity',
            'target': 'current'
        }

    def _compute_vehicle_booking_count(self):
        """Compute Vehicle Booking Count"""
        for rec in self:
            rec.vehicle_booking_count = self.env['vehicle.booking'].search_count(
                [('register_vehicle_id', '=', rec.id)])

    def action_view_vehicle_bookings(self):
        """Views vehicle Bookings"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vehicle Bookings'),
            'res_model': 'vehicle.booking',
            'domain': [('register_vehicle_id', '=', self.id)],
            'context': {
                'create': False
            },
            'view_mode': 'kanban,list,form,pivot,search,activity',
            'target': 'current'
        }


class ServiceHistory(models.Model):
    """Service History"""
    _name = 'service.history'
    _description = __doc__
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_service_display_name', store=True)
    odometer = fields.Float(string="Last Odometer")
    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
    ], default='kilometers')
    service_date = fields.Date(string="Date")
    register_vehicle_id = fields.Many2one('register.vehicle', ondelete='cascade')

    @api.constrains('odometer')
    def _check_odometer(self):
        """Check Odometer Value"""
        for record in self:
            if record.odometer <= 0:
                raise ValidationError(_("Odometer value must be greater than zero."))

    @api.depends(
        'register_vehicle_id.vehicle_brand_id',
        'register_vehicle_id.vehicle_model_id',
        'register_vehicle_id.registration_no',
        'service_date')
    def _compute_service_display_name(self):
        """Compute Service Display Name"""
        for rec in self:
            register_vehicle = rec.register_vehicle_id
            brand_name = register_vehicle.vehicle_brand_id.name or ''
            model_name = register_vehicle.vehicle_model_id.name or ''
            registration_no = register_vehicle.registration_no or ''
            date = rec.service_date
            rec.display_name = f"{brand_name}/{model_name}/{registration_no} / {date}"

    @api.constrains('odometer', 'service_date', 'register_vehicle_id')
    def _check_odometer(self):
        """Check odometer value"""
        for rec in self:
            today_date = fields.Date.today()

            if rec.register_vehicle_id and rec.odometer and rec.service_date:

                last_record = self.search([
                    ('register_vehicle_id', '=', rec.register_vehicle_id.id),
                    ('id', '!=', rec.id)
                ], order="odometer desc", limit=1)

                if last_record:
                    # Check odometer value
                    if rec.odometer <= last_record.odometer:
                        raise ValidationError(
                            f"Odometer value '{rec.odometer}' cannot be less than the last recorded value "
                            f"'{last_record.odometer}' for this vehicle.")

                    # Check service date
                    if rec.service_date < last_record.service_date:
                        raise ValidationError(
                            f"Service Date '{rec.service_date}' cannot be earlier than "
                            f"the last recorded Service Date '{last_record.service_date}' "
                            f"for this vehicle.")

                # Check that service date is not before today
                if rec.service_date < today_date:
                    raise ValidationError(
                        f"Service Date '{rec.service_date}' cannot be before today's date "
                        f"'{today_date}'.")
