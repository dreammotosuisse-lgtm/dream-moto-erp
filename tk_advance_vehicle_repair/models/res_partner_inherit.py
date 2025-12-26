# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, _


class VehicleCustomer(models.Model):
    """Vehicle Customer"""
    _inherit = 'res.partner'
    _description = __doc__

    vehicle_count = fields.Integer(string="Vehicles", compute='_compute_vehicle_count')

    def _compute_vehicle_count(self):
        """Customer Vehicle Count"""
        for rec in self:
            rec.vehicle_count = self.env['register.vehicle'].search_count(
                [('customer_id', '=', rec.id)])

    def action_view_vehicle_details(self):
        """Customer Vehicles Views"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vehicles'),
            'res_model': 'register.vehicle',
            'domain': [('customer_id', '=', self.id)],
            'context': {
                'default_customer_id': self.id,
            },
            'view_mode': 'list,form',
            'target': 'current'
        }
