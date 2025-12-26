# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ..utils import _display_adv_notification


class UpdateServiceInfo(models.TransientModel):
    """Update Service Info"""
    _name = 'update.service.info'
    _description = __doc__

    odometer = fields.Float(string="Odometer")
    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
    ], default='kilometers')
    service_date = fields.Date(string="Date", default=fields.Date.today())
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")
    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card")

    @api.constrains('odometer')
    def _check_odometer(self):
        """Check Odometer Value"""
        for record in self:
            if record.odometer <= 0:
                raise ValidationError(_("Odometer value must be greater than zero."))

    @api.model
    def default_get(self, fields_list):
        """Default record"""
        default_data = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if active_model == 'repair.job.card' and active_id:
            job_card = self.env['repair.job.card'].browse(active_id)
            default_data.update({
                'repair_job_card_id': job_card.id,
                'odometer': job_card.odometer,
                'odometer_unit': job_card.odometer_unit,
            })
        elif active_model == 'inspection.job.card' and active_id:
            job_card = self.env['inspection.job.card'].browse(active_id)
            default_data.update({
                'inspection_job_card_id': job_card.id,
                'odometer': job_card.odometer,
                'odometer_unit': job_card.odometer_unit,
            })
        return default_data

    def action_update_service_info(self):
        """Update Service info Record"""
        job_card = self.repair_job_card_id or self.inspection_job_card_id

        if not job_card:
            message = _display_adv_notification(
                message='No Job Card found for updating service info.',
                message_type='warning')
            return message

        if job_card.vehicle_from == 'new':
            message = _display_adv_notification(
                message='Vehicle is marked as new, no service history update required.',
                message_type='warning')
            return message

        if job_card.vehicle_from == 'customer_vehicle':
            if not job_card.register_vehicle_id:
                message = _display_adv_notification(
                    message='No registered vehicle is linked to this job card.',
                    message_type='info')
                return message
            service_history = self.env['service.history'].create({
                'odometer': self.odometer,
                'odometer_unit': self.odometer_unit,
                'service_date': self.service_date,
                'register_vehicle_id': job_card.register_vehicle_id.id,
            })
            job_card.odometer = self.odometer
            job_card.odometer_unit = self.odometer_unit
            job_card.service_history_id = service_history.id

        elif job_card.vehicle_from == 'fleet_vehicle':
            if not job_card.fleet_vehicle_id:
                message = _display_adv_notification(
                    message='No fleet vehicle is linked to this job card.',
                    message_type='info')
                return message
            fleet_odometer = self.env['fleet.vehicle.odometer'].create({
                'value': self.odometer,
                'unit': self.odometer_unit,
                'date': self.service_date,
                'vehicle_id': job_card.fleet_vehicle_id.id,
            })
            job_card.odometer = self.odometer
            job_card.odometer_unit = self.odometer_unit
            job_card.fleet_odometer_history_id = fleet_odometer.id
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': _("Service information has been updated successfully."),
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
