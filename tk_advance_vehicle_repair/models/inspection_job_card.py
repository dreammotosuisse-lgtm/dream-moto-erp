# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ..utils import _display_adv_notification


class InspectionImage(models.Model):
    """Inspection Image"""
    _name = "inspection.image"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary()
    name = fields.Char(required=True, translate=True, size=32)
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete='cascade')


class InspectionJobCard(models.Model):
    """Inspection Job Card"""
    _name = 'inspection.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'inspection_number'

    inspection_number = fields.Char(string='Inspection No', readonly=True,
                                    default=lambda self: _('New'), copy=False)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand")
    vehicle_model_id = fields.Many2one('vehicle.model', string="Model",
                                       domain="[('vehicle_brand_id', '=', vehicle_brand_id)]")
    vehicle_fuel_type_id = fields.Many2one('vehicle.fuel.type', string="Fuel Type")
    registration_no = fields.Char(translate=True)
    vin_no = fields.Char(string="VIN No.", translate=True)
    odometer = fields.Float(string="Last Odometer")
    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
    ], default='kilometers')
    transmission_type = fields.Selection([
        ('manual', "Manual"),
        ('automatic', "Automatic"),
        ('cvt', "CVT")])
    service_history_id = fields.Many2one('service.history')
    fleet_odometer_history_id = fields.Many2one('fleet.vehicle.odometer')

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(translate=True)
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one("res.country.state", string="State",
                               domain="[('country_id', '=?', country_id)]")
    zip = fields.Char()
    phone = fields.Char(translate=True)
    email = fields.Char(translate=True)
    customer_observation = fields.Text(translate=True)
    responsible_id = fields.Many2one(
        'res.users', string="Inspected By",
        domain=lambda self: [('all_group_ids', 'in', [self.env.ref('base.group_user').id])])

    inspection_type = fields.Selection(
        [('full_inspection', "Full Inspection"),
         ('specific_inspection', "Specific Inspection")],
        default='specific_inspection', string="Type of Inspection")

    inspect_type = fields.Selection([
        ('only_inspection', "Only Inspection"),
        ('inspection_and_repair', "Inspection + Repair")],
        string="Job Card Type")

    vehicle_booking_id = fields.Many2one('vehicle.booking', compute="_compute_vehicle_booking",
                                         string="Booking No")
    inspection_date = fields.Date(string="Date", default=fields.Date.today)
    inspection_charge_type = fields.Selection([
        ('free', "Free"),
        ('paid', "Paid")],
        default='paid', string="Inspection Charges Type")
    inspection_charge = fields.Monetary(string="Inspection Charges")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")

    # Part Assessment
    part_assessment = fields.Boolean()
    wd = fields.Boolean(string="4WD")
    abs = fields.Boolean(string="ABS")
    awd = fields.Boolean(string="AWD")
    gps = fields.Boolean(string="GPS")
    stereo = fields.Boolean()
    bed_liner = fields.Boolean(string="Bedliner")
    wide_tires = fields.Boolean()
    power_locks = fields.Boolean()
    power_seats = fields.Boolean()
    power_windows = fields.Boolean()
    running_boards = fields.Boolean()
    roof_rack = fields.Boolean()
    camper_shell = fields.Boolean()
    sport_wheels = fields.Boolean()
    tilt_wheel = fields.Boolean()
    cruise_control = fields.Boolean()
    cvt_transmission = fields.Boolean(string="CVT Transmission")
    infotainment_system = fields.Boolean()
    moon_sun_roof = fields.Boolean(string="Moon or Sun Roof")
    rear_sliding_window = fields.Boolean()
    rear_window_wiper = fields.Boolean()
    rear_lift_gate = fields.Boolean(string="Rear Liftgate")
    air_conditioning = fields.Boolean()
    leather_interior = fields.Boolean()
    towing_package = fields.Boolean()
    auto_transmission = fields.Boolean(string="Automatic Transmission")
    am_fm_radio = fields.Boolean(string="AM / FM / Sirius Radio")
    cd_usb_bluetooth = fields.Boolean(string="CD / USB / Bluetooth")
    luxury_sport_pkg = fields.Boolean(string="Luxury / Sport pkg.")
    other = fields.Boolean()

    # Inner Body Inspection
    inner_body_inspection = fields.Boolean()
    interior_item_condition_ids = fields.One2many(comodel_name='interior.item.condition',
                                                  inverse_name='inspection_job_card_id',
                                                  string="Interior Item")

    # Outer Body Inspection
    outer_body_inspection = fields.Boolean()
    vehicle_condition_line_ids = fields.One2many(comodel_name='vehicle.condition.line',
                                                 inverse_name='inspection_job_card_id',
                                                 string="Exterior Item")

    # Mechanical Condition
    mechanical_condition = fields.Boolean()
    mechanical_item_condition_ids = fields.One2many(comodel_name='mechanical.item.condition',
                                                    inverse_name='inspection_job_card_id',
                                                    string="Mechanical Item")

    # Vehicle Components
    vehicle_component = fields.Boolean()
    vehicle_components_ids = fields.One2many(comodel_name='vehicle.components',
                                             inverse_name='inspection_job_card_id',
                                             string=" Vehicle Component")

    # Vehicle Fluids
    vehicle_fluid = fields.Boolean()
    vehicle_fluids_ids = fields.One2many(comodel_name='vehicle.fluids',
                                         inverse_name='inspection_job_card_id',
                                         string=" Vehicle Fluid")

    # Tyre Inspection
    tyre_inspection = fields.Boolean(string="Tire Inspection")
    tyre_inspection_ids = fields.One2many(comodel_name='tyre.inspection',
                                          inverse_name='inspection_job_card_id',
                                          string="Vehicle Tire")

    vehicle_spare_part_ids = fields.One2many(comodel_name='vehicle.spare.part',
                                             inverse_name='inspection_job_card_id',
                                             string="Required Spare Part")
    inspection_repair_team_ids = fields.One2many(comodel_name='inspection.repair.team',
                                                 inverse_name='inspection_job_card_id',
                                                 string="Required Service")
    repair_job_card_id = fields.Many2one('repair.job.card',
                                         string="Repair Job Card")

    part_price = fields.Monetary(compute="_compute_spare_part_price")
    service_charge = fields.Monetary(compute="_compute_service_charge",
                                     string="Service Charges")
    sub_total = fields.Monetary(compute="_compute_sub_total")

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_state = fields.Selection(related='sale_order_id.state',
                                        string="Order State")
    amount_total = fields.Monetary(related='sale_order_id.amount_total',
                                   string="Total Amount")
    sale_invoiced = fields.Monetary()

    check_list_template_id = fields.Many2one('checklist.template', string="Vehicle Checklist")
    inspection_checklist_ids = fields.One2many(comodel_name='inspection.checklist',
                                               inverse_name='inspection_job_card_id',
                                               string="Checklist")

    vehicle_from = fields.Selection(
        [('new', "New"),
         ('fleet_vehicle', "Vehicle from Fleet"),
         ('customer_vehicle', "Vehicle from Customer")],
        default='new')
    register_vehicle_id = fields.Many2one('register.vehicle', string="Registered Vehicle",
                                          domain="[('customer_id', '=', customer_id)]")
    is_registered_vehicle = fields.Boolean(string="Registered")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet")
    review_notes = fields.Text()
    date = fields.Date(string="Date of Signature")
    signature = fields.Binary(string="Authorized Signature")
    inspection_image_ids = fields.One2many(comodel_name='inspection.image',
                                           inverse_name='inspection_job_card_id')

    inspection_report_type = fields.Selection(
        [('advanced_inspection', "Advanced Inspection"),
         ('classic_inspection', "Classic Inspection")],
        default='advanced_inspection')

    # Classic Inspection Template
    classic_inspection_template_id = fields.Many2one(
        comodel_name='classic.inspection.template',
        domain="[('inspection_report_type', '=', inspection_report_type)]",
        string="Inspection Template")

    # Exterior Vehicle Part Template
    exterior_vehicle_part_ids = fields.One2many(comodel_name='exterior.vehicle.part',
                                                inverse_name='inspection_job_card_id')

    # Interior Vehicle Part Template
    interior_vehicle_part_ids = fields.One2many(comodel_name='interior.vehicle.part',
                                                inverse_name='inspection_job_card_id')

    # Under Hood Vehicle Part
    under_hood_vehicle_part_ids = fields.One2many(comodel_name='under.hood.vehicle.part',
                                                  inverse_name='inspection_job_card_id')

    # Under Vehicle Part
    under_vehicle_part_ids = fields.One2many(comodel_name='under.vehicle.part',
                                             inverse_name='inspection_job_card_id')

    # Fluids Vehicle Part
    fluids_vehicle_part_ids = fields.One2many(comodel_name='fluids.vehicle.part',
                                              inverse_name='inspection_job_card_id')

    # Vehicle Part Tires
    vehicle_part_tires_ids = fields.One2many(comodel_name='vehicle.part.tires',
                                             inverse_name='inspection_job_card_id')

    # Vehicle Brake Condition
    vehicle_brake_condition_ids = fields.One2many(comodel_name='vehicle.brake.condition',
                                                  inverse_name='inspection_job_card_id')

    is_scratch_report = fields.Boolean(string="Custom Scratch Report")
    scratch_report_id = fields.Many2one('scratch.report', string="Scratch Report")
    quote_mail_send = fields.Boolean()
    is_skip_quotation = fields.Boolean(string="Skip Quotation")
    inspection_delivery_orders = fields.Integer(compute='_compute_inspection_delivery_orders')
    inspection_invoices = fields.Integer(compute='_compute_inspection_invoices')
    is_vehicle_under_warranty = fields.Boolean(string="Vehicle Under Warranty")
    stages = fields.Selection(
        [('a_draft', "New"),
         ('b_in_progress', "In Progress"),
         ('in_review', "In Review"),
         ('reject', "Reject"),
         ('c_complete', "Completed"),
         ('d_cancel', "Cancelled"),
         ('locked', "Locked")],
        default='a_draft', group_expand='_expand_groups', tracking=True, string="Status")


    @api.model_create_multi
    def create(self, vals_list):
        """ Create Method """
        for vals in vals_list:
            if vals.get('inspection_number', _('New')) == _('New'):
                vals['inspection_number'] = self.env['ir.sequence'].next_by_code(
                    'inspection.job.card') or _('New')
        res = super().create(vals_list)
        return res

    def write(self, vals_list):
        """ Write Method """
        rec = super().write(vals_list)
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
        return rec

    @api.model
    def _expand_groups(self, states, domain):
        return ['a_draft', 'b_in_progress', 'in_review', 'reject', 'c_complete', 'locked',
                'd_cancel']

    def a_draft_to_b_in_progress(self):
        """In Progress Stage"""
        self.stages = 'b_in_progress'

    def b_in_progress_to_in_review(self):
        """In Review Stage"""
        self.stages = 'in_review'

    def in_review_to_reject(self):
        """Reject Stage"""
        self.stages = 'reject'

    def reject_to_c_complete(self):
        """Validates all inspection checklists and ensures they are complete before proceeding."""

        # Checklist Template Check
        if any(not rec.is_check and not rec.display_type for rec in self.inspection_checklist_ids):
            message = _display_adv_notification(
                message='Please complete the checklist template',
                message_type='warning')
            return message

        # Reset is_skip_quotation if needed
        if (self.inspection_charge_type != 'paid'
                or self.inspect_type != 'inspection_and_repair'
                or self.is_skip_quotation):
            self.is_skip_quotation = False

        # Classic Inspection Checklist Check
        if self.inspection_report_type == 'classic_inspection':
            part_templates = [
                ('exterior_vehicle_part_ids', "Exterior parts"),
                ('interior_vehicle_part_ids', "Interior parts"),
                ('under_hood_vehicle_part_ids', "Under Hood Parts"),
                ('under_vehicle_part_ids', "Under Vehicle Parts"),
                ('vehicle_part_tires_ids', "Tires Conditions"),
                ('vehicle_brake_condition_ids', "Brakes Conditions"),
            ]

            for field_name, label in part_templates:
                part_lines = getattr(self, field_name)
                if any(not (rec.okay_for_now
                            or rec.further_attention
                            or rec.required_attention
                            or rec.not_inspected)
                       for rec in part_lines):
                    return _display_adv_notification(
                        message="Ensure all records in the '{}' template are checked.".format(
                            label),
                        message_type='warning'
                    )
            # Classic Inspection Fluids Checklist Check
            if any(not (rec.okay_for_now
                        or rec.further_attention
                        or rec.required_attention
                        or rec.not_inspected
                        or rec.filled)
                   for rec in self.fluids_vehicle_part_ids):
                return _display_adv_notification(
                    message="Ensure all records in the 'Vehicle Fluids' template are checked.",
                    message_type='warning')

        # Send email notification
        mail_template = self.env.ref('tk_advance_vehicle_repair.inspection_job_card_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        self.stages = 'c_complete'
        return True

    def c_complete_to_d_cancel(self):
        """Cancel Stage"""
        self.stages = 'd_cancel'

    def d_cancel_to_locked(self):
        """Locked Stage"""
        self.stages = 'locked'

    @api.onchange('fleet_vehicle_id', 'vehicle_from')
    def _onchange_fleet_vehicle(self):
        """Fleet Vehicle Details"""
        for rec in self:
            if rec.vehicle_from == 'fleet_vehicle' and rec.fleet_vehicle_id:
                rec.vehicle_brand_id = rec.fleet_vehicle_id.vehicle_brand_id.id
                rec.vehicle_model_id = rec.fleet_vehicle_id.vehicle_model_id.id
                rec.vehicle_fuel_type_id = rec.fleet_vehicle_id.vehicle_fuel_type_id.id
                rec.transmission_type = rec.fleet_vehicle_id.transmission_type
                rec.registration_no = rec.fleet_vehicle_id.license_plate
                rec.vin_no = rec.fleet_vehicle_id.vin_no
            else:
                # Reset fields if no valid customer vehicle
                rec.reset_vehicle_details()

    @api.onchange('register_vehicle_id', 'vehicle_from')
    def _onchange_customer_vehicle(self):
        """Customer Vehicle Details"""
        for rec in self:
            if rec.vehicle_from == 'customer_vehicle' and rec.register_vehicle_id:
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

    @api.onchange('check_list_template_id')
    def _onchange_check_list_template_id(self):
        """Inspection Checklist Template"""
        for rec in self:
            rec.inspection_checklist_ids = [(5, 0, 0)]  # Clear existing lines
            # Prepare new checklist items
            lines = []
            for data in rec.check_list_template_id.checklist_template_item_ids.sorted('sequence'):
                lines.append((0, 0, {
                    'name': data.name,
                    'sequence': data.sequence,
                    'display_type': data.display_type,
                }))
            # Update the checklist items
            rec.inspection_checklist_ids = lines

    @api.onchange('inspection_report_type')
    def _onchange_inspection_report_type(self):
        """Onchange inspection report type"""
        for rec in self:
            rec.inspection_type = 'specific_inspection'

    @api.onchange('inspection_report_type')
    def _onchange_inspection_temp(self):
        """Onchange inspection temp"""
        for rec in self:
            rec.classic_inspection_template_id = False

    @api.onchange('part_assessment', 'inner_body_inspection', 'outer_body_inspection',
                  'mechanical_condition', 'vehicle_component', 'vehicle_fluid', 'tyre_inspection')
    def _onchange_inspection_type(self):
        if all([
            self.part_assessment,
            self.inner_body_inspection,
            self.outer_body_inspection,
            self.mechanical_condition,
            self.vehicle_component,
            self.vehicle_fluid,
            self.tyre_inspection,
        ]):
            self.inspection_type = 'full_inspection'
        else:
            self.inspection_type = 'specific_inspection'

    @api.constrains('inspect_type')
    def _check_inspect_type(self):
        """Check Inspection Type"""
        for record in self:
            if not record.inspect_type:
                raise ValidationError(
                    _("Select inspection type: 'Only Inspection' or 'Inspection + Repair' Make a "
                      "choice to proceed."))

    @api.depends('inspection_repair_team_ids.service_charge')
    def _compute_service_charge(self):
        """Total Service Charges"""
        for rec in self:
            rec.service_charge = sum(
                service.service_charge for service in rec.inspection_repair_team_ids)

    @api.depends('vehicle_spare_part_ids.unit_price', 'vehicle_spare_part_ids.qty')
    def _compute_spare_part_price(self):
        """Total Spare Parts Price"""
        for rec in self:
            rec.part_price = sum(part.unit_price * part.qty for part in rec.vehicle_spare_part_ids)

    @api.depends('service_charge', 'part_price', 'inspection_charge')
    def _compute_sub_total(self):
        """Total Service and Spare Parts Price"""
        for rec in self:
            rec.sub_total = rec.service_charge + rec.part_price + rec.inspection_charge

    def _compute_vehicle_booking(self):
        """Vehicle Booking Details"""
        for rec in self:
            vehicle_booking_id = self.env['vehicle.booking'].search(
                [('inspection_job_card_id', '=', rec.id)], limit=1)
            rec.vehicle_booking_id = vehicle_booking_id.id

    def action_create_vehicle_registration(self):
        """Link Vehicle to Customer"""
        if not self.vehicle_brand_id or not self.vehicle_model_id:
            message = _display_adv_notification(
                message="Please provide the vehicle name and model along with any other relevant"
                        " vehicle details.",
                message_type='warning')
            return message
        register_vehicle_id = self.env['register.vehicle'].create({
            'customer_id': self.customer_id.id,
            'vehicle_brand_id': self.vehicle_brand_id.id if self.vehicle_brand_id else False,
            'vehicle_model_id': self.vehicle_model_id.id if self.vehicle_model_id else False,
            'vehicle_fuel_type_id': (self.vehicle_fuel_type_id.id
                                     if self.vehicle_fuel_type_id else False),
            'registration_no': self.registration_no,
            'vin_no': self.vin_no,
            'transmission_type': self.transmission_type,
        })
        self.write({
            'register_vehicle_id': register_vehicle_id.id,
            'vehicle_from': 'customer_vehicle',
            'is_registered_vehicle': True
        })

    def create_repair_job_card(self):
        """ Create Repair Job Card """
        # Validate required fields
        if not self.vehicle_brand_id or not self.registration_no or not self.vehicle_model_id:
            message = _display_adv_notification(
                message="Required: Vehicle, Registration No., and Model information.",
                message_type='warning')
            return message
        # Create repair job card
        repair_job_card = self.env['repair.job.card'].create({
            "vehicle_brand_id": self.vehicle_brand_id.id if self.vehicle_brand_id else False,
            "vehicle_model_id": self.vehicle_model_id.id if self.vehicle_model_id else False,
            "vehicle_fuel_type_id": (self.vehicle_fuel_type_id.id
                                     if self.vehicle_fuel_type_id else False),
            "register_vehicle_id": (self.register_vehicle_id.id
                                    if self.register_vehicle_id else False),
            "fleet_vehicle_id": self.fleet_vehicle_id.id if self.fleet_vehicle_id else False,
            "registration_no": self.registration_no,
            "vin_no": self.vin_no,
            "transmission_type": self.transmission_type,
            "inspect_repair_date": self.inspection_date,
            "vehicle_from": self.vehicle_from,
            "is_registered_vehicle": self.is_registered_vehicle,
            "customer_id": self.customer_id.id,
            "street": self.street,
            "street2": self.street2,
            "city": self.city,
            "state_id": self.state_id.id,
            "country_id": self.country_id.id,
            "zip": self.zip,
            "phone": self.phone,
            "email": self.email,
            "repair_sale_order_id": self.sale_order_id.id,
            "repair_amount": self.amount_total,
            "repair_order_state": self.sale_order_state,
            "sub_total": self.sub_total,
            "is_skip_quotation": self.is_skip_quotation,
            "customer_observation": self.customer_observation,
            "is_vehicle_under_warranty": self.is_vehicle_under_warranty,
            "odometer": self.odometer,
            "odometer_unit": self.odometer_unit,
        })
        # Check Invoices
        if self.sale_order_id:
            invoices = self.env['account.move'].search([('inspection_job_card_id', '=', self.id)])
            if invoices:
                invoices.write({'repair_job_card_id': repair_job_card.id})
        # Update the sale order with the repair job card
        if self.sale_order_id:
            self.sale_order_id.write({'repair_job_card_id': repair_job_card.id})
        # Assign Repair Job Card to the current record
        self.repair_job_card_id = repair_job_card.id
        # Create spare parts entries
        for part in self.vehicle_spare_part_ids:
            self.env['vehicle.order.spare.part'].create({
                'product_id': part.product_id.id,
                'qty': part.qty,
                'unit_price': part.unit_price,
                'repair_job_card_id': repair_job_card.id
            })
        # Create service team entries
        for service in self.inspection_repair_team_ids:
            self.env['vehicle.service.team'].create({
                'vehicle_service_id': service.vehicle_service_id.id,
                'start_date': service.start_date,
                'end_date': service.end_date,
                'service_charge': service.service_charge,
                'repair_job_card_id': repair_job_card.id,
            })
        # Return the form view of the newly created repair job card
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Job Card'),
            'res_model': 'repair.job.card',
            'res_id': repair_job_card.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def _prepare_inspection_order_lines(self):
        """Prepare order lines for the inspection quotation based on the job card details."""
        order_line = []
        sequence_number = 1
        # Inspection charge section
        if self.inspect_type in ('only_inspection', 'inspection_and_repair'):
            if (self.inspection_charge_type == 'paid' and not self.inspection_charge
                    and not self.is_vehicle_under_warranty):
                message = _display_adv_notification(
                    message="Kindly include the inspection charge amount.",
                    message_type='warning'
                )
                return message, False
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Inspection Charges"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            order_line.append((0, 0, {
                'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_inspection').id,
                'name': _('Vehicle Inspection'),
                'price_unit': 0 if self.is_vehicle_under_warranty else self.inspection_charge,
                'sequence': sequence_number,
            }))
            sequence_number += 1

        # Repair parts and services section
        if self.inspect_type == 'inspection_and_repair':
            if not self.vehicle_spare_part_ids:
                message = _display_adv_notification(
                    message="Please add the necessary spare parts to the 'Required Vehicle Spare Parts' tab.",
                    message_type='warning'
                )
                return message, False
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Required Parts"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            for part in self.vehicle_spare_part_ids:
                order_line.append((0, 0, {
                    'product_id': part.product_id.id,
                    'product_uom_qty': part.qty,
                    'price_unit': 0 if self.is_vehicle_under_warranty else part.unit_price,
                    'sequence': sequence_number,
                }))
                sequence_number += 1
            if not self.inspection_repair_team_ids:
                message = _display_adv_notification(
                    message="Please add the necessary service to the 'Required Vehicle Services' tab.",
                    message_type='warning'
                )
                return message, False
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Required Services"),
                'sequence': sequence_number,
            }))
            sequence_number += 1
            for rec in self.inspection_repair_team_ids:
                product_id = (
                    rec.vehicle_service_id.product_id.id
                    if rec.vehicle_service_id.product_id
                    else self.env.ref('tk_advance_vehicle_repair.vehicle_service_charge').id
                )
                order_line.append((0, 0, {
                    'product_id': product_id,
                    'name': rec.vehicle_service_id.name,
                    'price_unit': 0 if self.is_vehicle_under_warranty else rec.service_charge,
                    'sequence': sequence_number,
                }))
                sequence_number += 1
        return order_line, True

    def _send_quotation_email(self):
        """Send the appropriate quotation email based on the inspection report type."""
        mail_template_ref = {
            'advanced_inspection': 'tk_advance_vehicle_repair.advanced_inspection_quotation_mail_template',
            'classic_inspection': 'tk_advance_vehicle_repair.classic_inspection_quotation_mail_template',
        }
        template_ref = mail_template_ref.get(self.inspection_report_type)
        if template_ref:
            mail_template = self.env.ref(template_ref, raise_if_not_found=False)
            if mail_template:
                mail_template.send_mail(self.id, force_send=True)

    def create_inspection_repair_quotation(self):
        """Create a new inspection and repair quotation."""
        order_line, valid_order_line = self._prepare_inspection_order_lines()
        if not valid_order_line:
            return order_line
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'inspection_job_card_id': self.id,
        })
        self.sale_order_id = sale_order.id
        # Send email
        self._send_quotation_email()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def skip_quotation(self):
        """Without email quotation create"""
        order_line, valid_order_line = self._prepare_inspection_order_lines()
        if not valid_order_line:
            return order_line
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'inspection_job_card_id': self.id,
        })
        self.sale_order_id = sale_order.id
        self.stages = 'in_review'
        self.is_skip_quotation = True
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def update_inspection_repair_quotation(self):
        """Update an existing inspection and repair quotation."""
        order_line, valid_order_line = self._prepare_inspection_order_lines()
        if not valid_order_line:
            return order_line
        self.sale_order_id.sudo().write({
            'order_line': [(5, 0, 0)] + order_line
        })
        # Send email quotation
        self._send_quotation_email()
        message = _display_adv_notification(
            message="Quotation is successfully updated",
            message_type='success')
        return message

    def _compute_inspection_delivery_orders(self):
        """Inspection delivery order"""
        for rec in self:
            picking_ids = rec.sale_order_id.picking_ids.ids if rec.sale_order_id else []
            rec.inspection_delivery_orders = len(picking_ids)

    def action_view_inspection_delivery(self):
        """View related Inspection Delivery Orders"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery'),
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.sale_order_id.picking_ids.ids)],
            'view_mode': 'list,form,kanban',
            'target': 'current',
            'context': {
                'create': False,
            }
        }

    def create_inspection_job_card_invoice(self):
        """Create invoice for inspection job card based on delivered products."""
        sale_advance_payment = self.env['sale.advance.payment.inv'].with_context(
            active_model='sale.order',
            active_id=self.sale_order_id.id
        ).sudo()

        invoice_wizard = sale_advance_payment.create({
            'advance_payment_method': 'delivered'
        })
        invoice = invoice_wizard._create_invoices(self.sale_order_id)
        return invoice

    def _compute_inspection_invoices(self):
        """Compute Inspection Invoices"""
        for rec in self:
            rec.inspection_invoices = self.env['account.move'].search_count(
                [('inspection_job_card_id', '=', rec.id)])

    def view_inspection_invoice(self):
        """View inspection invoice"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'domain': [('inspection_job_card_id', '=', self.id)],
            'view_mode': 'list,form',
            'target': 'current',
            'context': {
                'create': False
            },
        }

    @api.onchange('classic_inspection_template_id')
    def _onchange_classic_inspection_template_id(self):
        """Populate inspection lines based on the selected inspection template."""
        for rec in self:
            template = rec.classic_inspection_template_id
            # Ensure a template is selected
            if not template:
                # Clear existing classic inspections
                rec.exterior_vehicle_part_ids = [(5, 0, 0)]
                rec.interior_vehicle_part_ids = [(5, 0, 0)]
                rec.under_hood_vehicle_part_ids = [(5, 0, 0)]
                rec.under_vehicle_part_ids = [(5, 0, 0)]
                rec.fluids_vehicle_part_ids = [(5, 0, 0)]
                rec.vehicle_part_tires_ids = [(5, 0, 0)]
                rec.vehicle_brake_condition_ids = [(5, 0, 0)]
                # Clear existing advanced inspections
                rec.interior_item_condition_ids = [(5, 0, 0)]
                rec.vehicle_condition_line_ids = [(5, 0, 0)]
                rec.mechanical_item_condition_ids = [(5, 0, 0)]
                rec.vehicle_components_ids = [(5, 0, 0)]
                rec.vehicle_fluids_ids = [(5, 0, 0)]
                # Advance Inspection Boolean
                rec.inner_body_inspection = False
                rec.outer_body_inspection = False
                rec.mechanical_condition = False
                rec.vehicle_component = False
                rec.vehicle_fluid = False

            if rec.inspection_report_type == 'classic_inspection':
                # Populate parts if enabled in template
                if template.exterior_part:
                    rec.exterior_vehicle_part_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_exterior_part_ids
                    ]
                if template.interior_part:
                    rec.interior_vehicle_part_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_interior_part_ids
                    ]
                if template.under_hood_part:
                    rec.under_hood_vehicle_part_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_under_hood_part_ids
                    ]
                if template.under_vehicle_part:
                    rec.under_vehicle_part_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_under_vehicle_part_ids
                    ]
                if template.is_fluid:
                    rec.fluids_vehicle_part_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_fluid_ids
                    ]
                if template.is_tire_condition:
                    rec.vehicle_part_tires_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_tire_ids
                    ]
                if template.is_brake_condition:
                    rec.vehicle_brake_condition_ids = [(5, 0, 0)] + [
                        (0, 0, {'vehicle_part_info_id': part.id})
                        for part in template.classic_brake_condition_ids
                    ]

            elif rec.inspection_report_type == 'advanced_inspection':
                # Advance Inspection Boolean
                rec.inner_body_inspection = False
                rec.outer_body_inspection = False
                rec.mechanical_condition = False
                rec.vehicle_component = False
                rec.vehicle_fluid = False
                # Populate component and fluid if enabled in template
                if template.is_interior_item:
                    rec.interior_item_condition_ids = [(5, 0, 0)] + [
                        (0, 0, {
                            'vehicle_item_id': part.id,
                        })
                        for part in template.advance_interior_item_ids
                    ]
                    rec.inner_body_inspection = True
                if template.is_exterior_item:
                    rec.vehicle_condition_line_ids = [(5, 0, 0)] + [
                        (0, 0, {
                            'vehicle_view': part.vehicle_view,
                            'vehicle_condition_location_id': part.vehicle_condition_location_id.id,
                        })
                        for part in template.advance_exterior_item_ids
                    ]
                    rec.outer_body_inspection = True
                if template.is_mechanical_item:
                    rec.mechanical_item_condition_ids = [(5, 0, 0)] + [
                        (0, 0, {
                            'vehicle_item_id': part.id,
                        })
                        for part in template.advance_mechanical_item_ids
                    ]
                    rec.mechanical_condition = True
                if template.is_vehicle_component:
                    rec.vehicle_components_ids = [(5, 0, 0)] + [
                        (0, 0, {
                            'vehicle_component_id': part.id,
                            'c_vehicle_side': part.compo_vehicle_side
                        })
                        for part in template.advance_vehicle_component_ids
                    ]
                    rec.vehicle_component = True
                if template.is_vehicle_fluid:
                    rec.vehicle_fluids_ids = [(5, 0, 0)] + [
                        (0, 0, {
                            'vehicle_fluid_id': part.id,
                            'f_vehicle_side': part.fluid_vehicle_side
                        })
                        for part in template.advance_vehicle_fluid_ids
                    ]
                    rec.vehicle_fluid = True

    @api.constrains('inspection_type', 'inner_body_inspection', 'outer_body_inspection',
                    'tyre_inspection', 'mechanical_condition', 'vehicle_component', 'vehicle_fluid')
    def _check_inspection_job_card_check(self):
        """Ensure at least one value is added when boolean are selected."""
        for record in self:
            if record.inspection_type == 'specific_inspection':
                if record.inner_body_inspection and not record.interior_item_condition_ids:
                    raise ValidationError(
                        _("Please add at least one 'Vehicle Body Inner Conditions' when 'Inner Body Inspection' is selected."))
                if record.outer_body_inspection and not record.vehicle_condition_line_ids:
                    raise ValidationError(
                        _("Please add at least one 'Vehicle Body Outer Conditions' when 'Outer Body Inspection' is selected."))
                if record.tyre_inspection and not record.tyre_inspection_ids:
                    raise ValidationError(
                        _("Please add at least one 'Tires Inspections' when 'Tire Inspection' is selected."))
                if record.mechanical_condition and not record.mechanical_item_condition_ids:
                    raise ValidationError(
                        _("Please add at least one 'Mechanical Conditions' when 'Mechanical Condition' is selected."))
                if record.vehicle_component and not record.vehicle_components_ids:
                    raise ValidationError(
                        _("Please add at least one 'Vehicle Components' when 'Vehicle Component' is selected."))
                if record.vehicle_fluid and not record.vehicle_fluids_ids:
                    raise ValidationError(
                        _("Please add at least one 'Vehicle Fluids' when 'Vehicle Fluid' is selected."))

    def check_inspection_report_type(self, boolean_field):
        """Check inspection report type"""
        if self.inspection_report_type != 'advanced_inspection':
            return False
        record = getattr(self, boolean_field, None)
        return self.inspection_type == 'full_inspection' or (
                self.inspection_type == 'specific_inspection' and record)

    @api.ondelete(at_uninstall=False)
    def _prevent_unlink(self):
        """Unlink Method"""
        for rec in self:
            if rec.stages == 'locked':
                raise ValidationError(_('You cannot delete the locked order.'))
