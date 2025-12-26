# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime
import secrets

import pytz

from odoo import models, fields, api, _
from ..utils import _display_adv_notification


class VehicleBooking(models.Model):
    """Vehicle Booking"""
    _name = 'vehicle.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'booking_number'

    # Booking Info
    booking_number = fields.Char(string='Booking No', readonly=True, default=lambda self: _('New'),
                                 copy=False)
    booking_date = fields.Date(default=fields.Date.today)
    booking_source = fields.Selection([
        ('direct', "Direct"),
        ('website', "Website")],
        default='direct')
    booking_type = fields.Selection([
        ('only_inspection', "Only Vehicle Inspection"),
        ('only_repair', "Only Vehicle Repair"),
        ('inspection_and_repair', "Vehicle Inspection + Vehicle Repair")],
        default='only_inspection')
    booking_stages = fields.Selection([
        ('draft', "New"),
        ('vehicle_inspection', "Vehicle Inspection"),
        ('vehicle_repair', "Vehicle Repair"),
        ('vehicle_inspection_repair', "Inspection + Repair"),
        ('cancel', "Cancelled")],
        default='draft', string="Status", group_expand='_expand_groups', tracking=True)

    # Vehicle Info
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    registration_no = fields.Char(string="Registration No.", translate=True)
    vin_no = fields.Char(string="VIN No.", translate=True)
    transmission_type = fields.Selection(
        [('manual', "Manual"),
         ('automatic', "Automatic"),
         ('cvt', "CVT")])
    vehicle_from = fields.Selection([
        ('new', "New"),
        ('fleet_vehicle', "Vehicle from Fleet"),
        ('customer_vehicle', "Vehicle from Customer")], default='new')
    is_registered_vehicle = fields.Boolean(string="Registered")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet")
    register_vehicle_id = fields.Many2one('register.vehicle', string="Registered Vehicle",
                                          domain="[('customer_id', '=', customer_id)]")

    # Customer Info
    customer_id = fields.Many2one('res.partner', string='Customer')
    street = fields.Char(translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(translate=True)
    zip = fields.Char()
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one("res.country.state", string="State",
                               domain="[('country_id', '=?', country_id)]")
    phone = fields.Char(translate=True)
    email = fields.Char(translate=True)
    customer_observation = fields.Text(translate=True)

    # Appointments
    booking_appointment_id = fields.Many2one('booking.appointment', string="Appointment Day")
    booking_appointment_slot_ids = fields.Many2many('booking.appointment.slot',
                                                    compute='_compute_available_slots',
                                                    string='Available Slots')
    booking_appointment_slot_id = fields.Many2one(
        'booking.appointment.slot', string="Booking Slot",
        domain="[('id', 'in', booking_appointment_slot_ids)]")

    # Job Cards
    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card")
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")

    # Services & Parts
    vehicle_service_ids = fields.Many2many('vehicle.service', string="Services")
    vehicle_spare_part_ids = fields.Many2many('product.product', string='Spare Parts',
                                              domain="[('is_vehicle_part', '=', True)]")

    # Other Info
    estimate_cost = fields.Monetary()
    responsible_id = fields.Many2one(
        'res.users', string="Responsible",
        domain=lambda self: [('all_group_ids', 'in', [self.env.ref('base.group_user').id])])
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    access_token = fields.Char()

    # CREATE / WRITE Methods
    @api.model_create_multi
    def create(self, vals_list):
        """Create vehicle booking record"""
        records = super().create(vals_list)
        for record in records:
            if record.booking_number == _('New'):
                record.booking_number = self.env['ir.sequence'].next_by_code(
                    'vehicle.booking') or _('New')
            # Generate a URL-safe access token without underscores
            token = secrets.token_urlsafe(12).replace('_', '-')
            record.access_token = token
        return records

    def write(self, vals):
        """Write record"""
        result = super().write(vals)
        self.customer_id.write({
            'name': self.customer_id.name,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'zip': self.zip,
            'phone': self.phone,
            'email': self.email,
        })
        return result

    @api.model
    def generate_missing_access_tokens(self):
        """Cron to generate access tokens for old records"""
        bookings = self.search([('access_token', '=', False)])
        for record in bookings:
            token = secrets.token_urlsafe(12).replace('_', '-')
            record.access_token = token

    @api.model
    def _expand_groups(self, states, domain):
        return ['draft', 'vehicle_inspection', 'vehicle_repair', 'vehicle_inspection_repair',
                'cancel']

    def _check_available_slots(self):
        """Check available slots only if slot is selected"""
        self.ensure_one()
        # Skip check if no appointment slot is selected
        if not self.booking_appointment_slot_id:
            return True
        booking_slots = self.env['vehicle.booking'].search([
            ('booking_appointment_slot_id', '=', self.booking_appointment_slot_id.id),
            ('booking_stages', 'not in', ['draft', 'cancel']),
            ('booking_date', '=', self.booking_date)
        ])
        if booking_slots:
            message = _display_adv_notification(
                message='Booking slot is already booked. Please choose another slot.',
                message_type='warning')
            return message
        return True

    def _get_common_vehicle_fields(self):
        """Shared vehicle-related fields for job card creation."""
        return {
            "vehicle_brand_id": self.vehicle_brand_id.id if self.vehicle_brand_id else False,
            "vehicle_model_id": self.vehicle_model_id.id if self.vehicle_model_id else False,
            "vehicle_fuel_type_id":
                self.vehicle_fuel_type_id.id if self.vehicle_fuel_type_id else False,
            "registration_no": self.registration_no,
            "fleet_vehicle_id": self.fleet_vehicle_id.id,
            "register_vehicle_id": self.register_vehicle_id.id,
            "vehicle_from": self.vehicle_from,
            "is_registered_vehicle": self.is_registered_vehicle,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "customer_observation": self.customer_observation,
        }

    def draft_to_vehicle_inspection(self):
        """Create Vehicle Inspection Job Card"""
        result = self._check_available_slots()
        if result is not True:
            return result
        values = self._get_common_vehicle_fields()
        values.update({
            "inspection_date": self.booking_date,
            "inspect_type": self.booking_type,
            "responsible_id": self.env.user.id if self.env.user.has_group(
                'tk_advance_vehicle_repair.vehicle_repair_technician') else False,
        })
        inspection_job_card = self.env['inspection.job.card'].create(values)
        self.write({
            'inspection_job_card_id': inspection_job_card.id,
            'booking_stages': 'vehicle_inspection',
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Job Card'),
            'res_model': 'inspection.job.card',
            'res_id': inspection_job_card.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_inspection_to_vehicle_repair(self):
        """Create Vehicle Repair Job Card"""
        result = self._check_available_slots()
        if result is not True:
            return result
        values = self._get_common_vehicle_fields()
        values.update({"inspect_repair_date": self.booking_date})
        repair_job_card = self.env['repair.job.card'].create(values)
        self.write({
            'repair_job_card_id': repair_job_card.id,
            'booking_stages': 'vehicle_repair',
        })
        # Add required spare parts
        for part in self.vehicle_spare_part_ids:
            self.env['vehicle.order.spare.part'].create({
                'product_id': part.id,
                'unit_price': part.lst_price,
                'repair_job_card_id': repair_job_card.id,
            })
        # Add required services
        for service in self.vehicle_service_ids:
            self.env['vehicle.service.team'].create({
                'vehicle_service_id': service.id,
                'service_charge': service.lst_price,
                'repair_job_card_id': repair_job_card.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Job Card'),
            'res_model': 'repair.job.card',
            'res_id': repair_job_card.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_repair_to_vehicle_inspection_repair(self):
        """Create Combined Inspection and Repair Job Card"""
        result = self._check_available_slots()
        if result is not True:
            return result
        values = self._get_common_vehicle_fields()
        values.update({
            "inspection_date": self.booking_date,
            "inspect_type": self.booking_type,
            "responsible_id": self.env.user.id if self.env.user.has_group(
                'tk_advance_vehicle_repair.vehicle_repair_technician') else False,
        })
        inspection_job_card = self.env['inspection.job.card'].create(values)
        self.write({
            'inspection_job_card_id': inspection_job_card.id,
            'booking_stages': 'vehicle_inspection_repair',
        })
        # Add spare parts
        for part in self.vehicle_spare_part_ids:
            self.env['vehicle.spare.part'].create({
                'product_id': part.id,
                'unit_price': part.lst_price,
                'inspection_job_card_id': inspection_job_card.id,
            })
        # Add services
        for service in self.vehicle_service_ids:
            self.env['inspection.repair.team'].create({
                'vehicle_service_id': service.id,
                'service_charge': service.lst_price,
                'inspection_job_card_id': inspection_job_card.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inspection Job Card'),
            'res_model': 'inspection.job.card',
            'res_id': inspection_job_card.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def vehicle_inspection_repair_to_cancel(self):
        """Cancel Stage"""
        self.booking_stages = 'cancel'

    @api.onchange('booking_date')
    def _onchange_booking_days(self):
        """Appointment Day Wise Slot Visible"""
        if self.booking_date:
            day = self.booking_date.strftime("%A").lower()
            appointment = self.env['booking.appointment'].sudo().search(
                [('appointment_day', '=', day)], limit=1)
            self.booking_appointment_id = appointment.id

    @api.onchange('booking_date')
    def _onchange_booking_date(self):
        """Onchange booking date"""
        for rec in self:
            rec.booking_appointment_slot_id = False

    @api.depends('booking_appointment_id', 'booking_date')
    def _compute_available_slots(self):
        """Compute available slots for selected appointment day"""
        for record in self:
            if record.booking_appointment_id and record.booking_date:
                all_slots = self.env['booking.appointment.slot'].search([
                    ('booking_appointment_id', '=', record.booking_appointment_id.id)
                ])
                user_tz = self.env.user.tz or 'UTC'
                now_dt = datetime.now(pytz.timezone(user_tz))
                today = now_dt.date()
                now_time = now_dt.time()

                now_time_float = now_time.hour + now_time.minute / 60.0

                # Find already booked slots
                booked_slots = self.env['vehicle.booking'].sudo().search([
                    ('booking_stages', 'not in', ['draft', 'cancel']),
                    ('booking_date', '=', record.booking_date),
                    ('booking_appointment_slot_id', '!=', False),
                ]).mapped('booking_appointment_slot_id')
                # Remove booked slots
                available_slots = all_slots - booked_slots
                # If booking date is today, filter out past slots
                if record.booking_date == today:
                    available_slots = available_slots.filtered(
                        lambda slot: slot.from_time > now_time_float)
                record.booking_appointment_slot_ids = available_slots
            else:
                record.booking_appointment_slot_ids = False

    @api.onchange('fleet_vehicle_id', 'vehicle_from')
    def _onchange_fleet_vehicle(self):
        """Update details when a fleet vehicle is selected."""
        for rec in self:
            if rec.vehicle_from == 'fleet_vehicle' and rec.fleet_vehicle_id:
                # Update fields based on the fleet vehicle
                rec.vehicle_brand_id = rec.fleet_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.fleet_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.fleet_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.fleet_vehicle_id.transmission_type
                rec.registration_no = rec.fleet_vehicle_id.license_plate
                rec.vin_no = rec.fleet_vehicle_id.vin_no
            else:
                # Reset fields if no valid fleet vehicle
                rec.reset_vehicle_details()

    @api.onchange('register_vehicle_id', 'vehicle_from')
    def _onchange_customer_vehicle(self):
        """Update details when a customer vehicle is selected."""
        for rec in self:
            if rec.vehicle_from == 'customer_vehicle' and rec.register_vehicle_id:
                # Update fields based on the customer vehicle
                rec.vehicle_brand_id = rec.register_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.register_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.register_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.register_vehicle_id.transmission_type
                rec.registration_no = rec.register_vehicle_id.registration_no
                rec.vin_no = rec.register_vehicle_id.vin_no
            else:
                # Reset fields if no valid customer vehicle
                rec.reset_vehicle_details()

    def reset_vehicle_details(self):
        """Helper method to reset vehicle details."""
        self.vehicle_brand_id = False
        self.vehicle_model_id = False
        self.vehicle_fuel_type_id = False
        self.transmission_type = ''
        self.registration_no = ''
        self.vin_no = ''

    @api.onchange('vehicle_brand_id')
    def _onchange_vehicle_brand_id(self):
        """Reset vehicle fuel type when the brand changes."""
        for rec in self:
            if not rec.vehicle_brand_id:
                rec.vehicle_fuel_type_id = False
                rec.vehicle_model_id = False

    @api.onchange('vehicle_model_id')
    def _onchange_vehicle_model_id(self):
        """Reset vehicle fuel type when the model changes."""
        for rec in self:
            if not rec.vehicle_model_id:
                rec.vehicle_fuel_type_id = False

    @api.onchange('customer_id')
    def _onchange_customer_details(self):
        """Customer Details"""
        for rec in self:
            rec.phone = rec.customer_id.phone
            rec.email = rec.customer_id.email
            rec.street = rec.customer_id.street
            rec.street2 = rec.customer_id.street2
            rec.city = rec.customer_id.city
            rec.state_id = rec.customer_id.state_id
            rec.country_id = rec.customer_id.country_id
            rec.zip = rec.customer_id.zip
            # Clear vehicle-related fields
            rec.register_vehicle_id = False
            rec.fleet_vehicle_id = False

    def action_create_vehicle_registration(self):
        """Link Vehicle to Customer"""
        register_vehicle_id = self.env['register.vehicle'].create({
            'customer_id': self.customer_id.id if self.customer_id else False,
            'vehicle_brand_id': self.vehicle_brand_id.id if self.vehicle_brand_id else False,
            'vehicle_model_id': self.vehicle_model_id.id if self.vehicle_model_id else False,
            'vehicle_fuel_type_id':
                self.vehicle_fuel_type_id.id if self.vehicle_fuel_type_id else False,
            'registration_no': self.registration_no,
            'vin_no': self.vin_no,
            'transmission_type': self.transmission_type,
        })
        self.write({
            'register_vehicle_id': register_vehicle_id.id,
            'vehicle_from': 'customer_vehicle',
            'is_registered_vehicle': True,
        })
        return True
