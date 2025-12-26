# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ..utils import _display_adv_notification


class RepairImage(models.Model):
    """Repair Image"""
    _name = "repair.image"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary()
    name = fields.Char(required=True, translate=True, size=32)
    repair_job_card_id = fields.Many2one('repair.job.card', ondelete='cascade')


class RepairJobCard(models.Model):
    """Repair Job Card"""
    _name = 'repair.job.card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Sequence No', readonly=True,
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
        'res.users',
        domain=lambda self: [('all_group_ids', 'in', [self.env.ref('base.group_user').id])],
        string="Responsible")

    inspect_repair_date = fields.Date(string="Date", default=fields.Date.today)
    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card",
                                             compute='_compute_vehicle_inspection_job_card')
    vehicle_booking_id = fields.Many2one('vehicle.booking', compute="_compute_vehicle_booking",
                                         string="Booking No")

    vehicle_order_spare_part_ids = fields.One2many(comodel_name='vehicle.order.spare.part',
                                                   inverse_name='repair_job_card_id')
    vehicle_service_team_ids = fields.One2many(comodel_name='vehicle.service.team',
                                               inverse_name='repair_job_card_id')

    part_price = fields.Monetary(compute="_compute_spare_part_price", store=True)
    service_charge = fields.Monetary(compute="_compute_service_charge",
                                     string="Service Charges", store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    sub_total = fields.Monetary(compute="_compute_sub_total")
    team_task_count = fields.Integer(compute="_compute_team_task_count", string="Task")
    repair_sale_order_id = fields.Many2one('sale.order', string=" Sale Order")
    repair_order_state = fields.Selection(related='repair_sale_order_id.state')
    repair_amount = fields.Monetary(related='repair_sale_order_id.amount_total',
                                    string=" Total Amount")
    repair_sale_invoiced = fields.Monetary()
    check_list_template_id = fields.Many2one('checklist.template',
                                             string="Vehicle Checklist")
    repair_checklist_ids = fields.One2many(comodel_name='repair.checklist',
                                           inverse_name='repair_job_card_id',
                                           string="Checklist")
    vehicle_from = fields.Selection(
        [('new', "New"),
         ('fleet_vehicle', "Vehicle from Fleet"),
         ('customer_vehicle', "Vehicle from Customer")], default='new')
    register_vehicle_id = fields.Many2one('register.vehicle', string="Registered Vehicle",
                                          domain="[('customer_id', '=', customer_id)]")
    is_registered_vehicle = fields.Boolean(string="Registered")
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Fleet")
    reject_reasons = fields.Text()
    date = fields.Date(string="Date of Signature")
    signature = fields.Binary(string="Authorized Signature")
    is_scratch_report = fields.Boolean(string="Custom Scratch Report")
    scratch_report_id = fields.Many2one('scratch.report', string="Scratch Report")
    repair_image_ids = fields.One2many(comodel_name='repair.image',
                                       inverse_name='repair_job_card_id')
    is_skip_quotation = fields.Boolean(string="Skip Quotation")
    repair_delivery_orders = fields.Integer(compute='_compute_repair_delivery_orders')
    repair_invoices = fields.Integer(compute='_compute_repair_invoices')
    is_vehicle_under_warranty = fields.Boolean(string="Vehicle Under Warranty")
    stages = fields.Selection(
        [('draft', "New"),
         ('assign_to_technician', "Assign to Technician"),
         ('in_diagnosis', "In Diagnosis"),
         ('supervisor_inspection', "In Supervisor Inspection"),
         ('reject', "Reject"),
         ('complete', "Completed"),
         ('hold', "Hold"),
         ('cancel', "Cancel"),
         ('locked', "Locked")],
        default='draft', string=" Status", group_expand='_expand_groups', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        """ Create Method """
        for vals in vals_list:
            if vals.get('sequence_number', _('New')) == _('New'):
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code(
                    'repair.job.card') or _('New')
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
        """ Expand Groups """
        return ['draft', 'assign_to_technician', 'in_diagnosis', 'supervisor_inspection', 'reject',
                'complete', 'hold', 'locked', 'cancel']

    def draft_to_assign_to_technician(self):
        """Required Services Check"""
        if not self.vehicle_service_team_ids:
            message = _display_adv_notification(
                message='Please choose the required service',
                message_type='warning')
            return message
        for record in self.vehicle_service_team_ids:
            if not record.service_team_id or not record.vehicle_service_team_members_ids:
                message = _display_adv_notification(
                    message='In service tab: Please assign a team and team members each listed service',
                    message_type='warning')
                return message
        self.stages = 'assign_to_technician'
        return True

    def assign_to_technician_to_in_diagnosis(self):
        """Check and create tasks for team members"""
        if self.vehicle_service_team_ids:
            for rec in self.vehicle_service_team_ids:
                if not rec.team_task_id:
                    rec.create_service_task()
        self.stages = 'in_diagnosis'

    def in_diagnosis_to_supervisor_inspection(self):
        """Team Task Check"""
        team_work_complete = all(rec.work_is_done for rec in self.vehicle_service_team_ids)
        if not team_work_complete:
            message = _display_adv_notification(
                message='Please complete all team tasks',
                message_type='warning')
            return message
        self.stages = 'supervisor_inspection'
        return True

    def supervisor_inspection_to_reject(self):
        """Move to Reject Stage"""
        for rec in self.vehicle_service_team_ids:
            if rec.team_task_id and rec.team_task_id.work_is_done:
                rec.team_task_id.work_is_done = False
            rec.end_date = False
        self.stages = 'reject'

    def reject_to_complete(self):
        """Checklist Template Check"""
        if any(not rec.is_check and not rec.display_type for rec in self.repair_checklist_ids):
            message = _display_adv_notification(
                message='Please complete the checklist template',
                message_type='warning')
            return message
        self.stages = 'complete'
        mail_template = self.env.ref('tk_advance_vehicle_repair.repair_job_card_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)
        return True

    def complete_to_hold(self):
        """Hold Stage"""
        self.stages = 'hold'

    def complete_to_locked(self):
        """Locked Stage"""
        self.stages = 'locked'

    def hold_to_cancel(self):
        """Cancel Stage"""
        self.stages = 'cancel'

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
        """Repair Checklist Template"""
        for rec in self:
            rec.repair_checklist_ids = [(5, 0, 0)]  # Clear existing lines
            # Prepare new checklist items
            lines = []
            for data in rec.check_list_template_id.checklist_template_item_ids.sorted('sequence'):
                lines.append((0, 0, {
                    'name': data.name,
                    'sequence': data.sequence,
                    'display_type': data.display_type,
                }))
            # Update the checklist items
            rec.repair_checklist_ids = lines

    @api.depends('vehicle_service_team_ids.service_charge')
    def _compute_service_charge(self):
        """Total Service Charges"""
        for rec in self:
            rec.service_charge = sum(
                service.service_charge for service in rec.vehicle_service_team_ids)

    @api.depends('vehicle_order_spare_part_ids.unit_price', 'vehicle_order_spare_part_ids.qty')
    def _compute_spare_part_price(self):
        """Total Spare Parts Price"""
        for rec in self:
            rec.part_price = sum(
                part.unit_price * part.qty for part in rec.vehicle_order_spare_part_ids)

    @api.depends('sub_total', 'service_charge', 'part_price')
    def _compute_sub_total(self):
        """Total Service and Spare Parts Price"""
        for rec in self:
            rec.sub_total = rec.service_charge + rec.part_price

    def _compute_vehicle_booking(self):
        """Vehicle Booking Details"""
        for rec in self:
            vehicle_booking_id = self.env['vehicle.booking'].search(
                [('repair_job_card_id', '=', rec.id)], limit=1)
            rec.vehicle_booking_id = vehicle_booking_id.id

    def action_create_vehicle_registration(self):
        """Link Vehicle to Customer"""
        if not self.vehicle_brand_id or not self.vehicle_model_id:
            message = _display_adv_notification(
                message='Please provide the vehicle name and model along with any other relevant'
                        ' vehicle details.',
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
        return True

    def _compute_team_task_count(self):
        """Task Count"""
        for rec in self:
            rec.team_task_count = self.env['project.task'].search_count(
                [('repair_job_card_id', '=', rec.id)])

    def view_team_tasks(self):
        """View Team Task"""
        team_task_ids = self.inspection_job_card_id.inspection_repair_team_ids.mapped(
            'team_task_id').ids
        domain = ['|', ('repair_job_card_id', '=', self.id), ('id', 'in', team_task_ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'list,form,kanban,calendar,pivot,graph,activity',
            'res_model': 'project.task',
            'domain': domain,
            'context': {
                'create': False,
            }
        }

    def _compute_vehicle_inspection_job_card(self):
        """Inspection Job Card ID"""
        inspection_job_card_id = self.env['inspection.job.card'].search(
            [('repair_job_card_id', '=', self.id)], limit=1)
        self.inspection_job_card_id = inspection_job_card_id.id

    def _prepare_repair_order_lines(self):
        """Prepare repair order"""
        order_line = []
        sequence = 1
        job_card = self.inspection_job_card_id
        # Add service charges
        if job_card:
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': _("Inspection Charges"),
                'sequence': sequence,
            }))
            sequence += 1
            order_line.append((0, 0, {
                'product_id': self.env.ref('tk_advance_vehicle_repair.vehicle_inspection').id,
                'name': _('Vehicle Inspection'),
                'price_unit': 0 if self.is_vehicle_under_warranty else job_card.inspection_charge,
                'sequence': sequence,
            }))
            sequence += 1
        # Add Spare Parts
        if self.vehicle_order_spare_part_ids:
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': "Required Parts",
                'sequence': sequence,
            }))
            sequence += 1
            for part in self.vehicle_order_spare_part_ids:
                order_line.append((0, 0, {
                    'product_id': part.product_id.id,
                    'product_uom_qty': part.qty,
                    'price_unit': 0 if self.is_vehicle_under_warranty else part.unit_price,
                    'sequence': sequence,
                }))
                sequence += 1
        # Add Services
        if self.vehicle_service_team_ids:
            order_line.append((0, 0, {
                'display_type': 'line_section',
                'name': "Required Services",
                'sequence': sequence,
            }))
            sequence += 1
            for service in self.vehicle_service_team_ids:
                product_id = (
                    service.vehicle_service_id.product_id.id
                    if service.vehicle_service_id.product_id
                    else self.env.ref('tk_advance_vehicle_repair.vehicle_service_charge').id
                )
                order_line.append((0, 0, {
                    'product_id': product_id,
                    'name': service.vehicle_service_id.name,
                    'price_unit': 0 if self.is_vehicle_under_warranty else service.service_charge,
                    'sequence': sequence,
                }))
                sequence += 1
        return order_line

    def _send_repair_quotation_email(self):
        """Send repair quotation mail"""
        mail_template = self.env.ref(
            'tk_advance_vehicle_repair.vehicle_repair_quotation_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)

    def action_repair_sale_order(self):
        """Action create repair sale order"""
        # Check for required data
        if not self.vehicle_order_spare_part_ids:
            message = _display_adv_notification(
                message="Please add the necessary spare parts to the 'Vehicle Spare Parts' tab.",
                message_type='warning')
            return message
        if not self.vehicle_service_team_ids:
            message = _display_adv_notification(
                message="Please add the necessary services.",
                message_type='warning')
            return message
        order_line = self._prepare_repair_order_lines()
        # Ensure order lines exist
        if not order_line:
            message = _display_adv_notification(
                message="The total value of the sale order cannot be zero. Please ensure all"
                        " required parts and services are correctly entered.",
                message_type='warning')
            return message
        # Create Sale Order
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'repair_job_card_id': self.id,
        })
        # Link sale order to job card
        self.write({
            'repair_sale_order_id': sale_order.id,
            'repair_sale_invoiced': sale_order.amount_total,
        })
        self._send_repair_quotation_email()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def update_repair_quotation(self):
        """Update repair quotation"""
        if self.repair_sale_order_id:
            self.repair_sale_order_id.order_line.sudo().unlink()
            self.repair_sale_order_id.write({
                'order_line': self._prepare_repair_order_lines(),
            })
        self._send_repair_quotation_email()
        message = _display_adv_notification(
            message="Quotation is successfully updated",
            message_type='success')
        return message

    def _compute_repair_delivery_orders(self):
        """Repair delivery order"""
        for rec in self:
            picking_ids = (rec.repair_sale_order_id.picking_ids.ids
                           if rec.repair_sale_order_id
                           else [])
            rec.repair_delivery_orders = len(picking_ids)

    def action_view_repair_delivery(self):
        """View related repair delivery orders"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery'),
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.repair_sale_order_id.picking_ids.ids)],
            'view_mode': 'list,form,kanban',
            'target': 'current',
            'context': {
                'create': False,
            }
        }

    def create_repair_job_card_invoice(self):
        """Create an invoice for the repair job card based on the related sale order."""
        sale_advance_payment = self.env['sale.advance.payment.inv'].with_context(
            active_model='sale.order',
            active_id=self.repair_sale_order_id.id
        ).sudo()
        # Create the invoice using 'delivered' method
        invoice_wizard = sale_advance_payment.create({
            'advance_payment_method': 'delivered'
        })
        invoices = invoice_wizard._create_invoices(self.repair_sale_order_id)
        if invoices:
            invoice = invoices[0]
            # Link the invoice to the current repair job card if not already linked
            if not invoice.repair_job_card_id:
                invoice.write({'repair_job_card_id': self.id})
            return invoice
        return False

    def _compute_repair_invoices(self):
        """Compute Repair Invoices"""
        for rec in self:
            rec.repair_invoices = self.env['account.move'].search_count(
                [('repair_job_card_id', '=', rec.id)])

    def view_repair_invoice(self):
        """View repair invoice"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'domain': [('repair_job_card_id', '=', self.id)],
            'view_mode': 'list,form',
            'target': 'current',
            'context': {
                'create': False
            },
        }

    @api.ondelete(at_uninstall=False)
    def _prevent_unlink(self):
        """Unlink Method"""
        for rec in self:
            if rec.stages == 'locked':
                raise ValidationError(_('You cannot delete the locked order.'))
