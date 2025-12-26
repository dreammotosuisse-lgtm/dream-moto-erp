# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class VehiclePartProductTemplate(models.Model):
    """Vehicle Part Product Template"""
    _inherit = 'product.template'
    _description = __doc__

    color = fields.Integer(default=1)
    is_vehicle_part = fields.Boolean(string="Vehicle Spare Part")


class VehicleServiceType(models.Model):
    """Vehicle Service Type"""
    _inherit = 'product.product'
    _description = __doc__
    _inherits = {'product.template': 'product_tmpl_id'}


class VehicleSparePart(models.Model):
    """Vehicle Spare part"""
    _name = 'vehicle.spare.part'
    _description = __doc__
    _rec_name = 'product_id'

    color = fields.Integer()
    product_id = fields.Many2one('product.product', domain="[('is_vehicle_part', '=', True)]",
                                 required=True, string='Spare Part')
    qty = fields.Integer(string="Quantity", default=1)
    unit_price = fields.Monetary()
    sub_total = fields.Monetary(compute='_compute_sub_total')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete="cascade")

    @api.onchange('product_id')
    def _onchange_spare_part_price(self):
        """Onchange Spare Parts Charges"""
        for rec in self:
            rec.unit_price = rec.product_id.lst_price

    @api.depends('qty', 'unit_price')
    def _compute_sub_total(self):
        """Total Spare Parts Charges"""
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price


class VehicleOrderSparePart(models.Model):
    """Vehicle Order Spare part"""
    _name = 'vehicle.order.spare.part'
    _description = __doc__
    _rec_name = 'product_id'

    color = fields.Integer()
    product_id = fields.Many2one('product.product', domain="[('is_vehicle_part', '=', True)]",
                                 required=True, string='Spare Part')
    qty = fields.Integer(string="Quantity", default=1)
    unit_price = fields.Monetary()
    sub_total = fields.Monetary(compute='_compute_sub_total')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    repair_job_card_id = fields.Many2one('repair.job.card', ondelete="cascade")
    vehicle_service_team_ids = fields.One2many(
        related='repair_job_card_id.vehicle_service_team_ids')
    valid_vehicle_service_ids = fields.Many2many('vehicle.service',
                                                 compute='_compute_valid_vehicle_services')
    vehicle_service_ids = fields.Many2many('vehicle.service', string="Services",
                                           domain="[('id', 'in', valid_vehicle_service_ids)]")

    @api.depends('vehicle_service_team_ids')
    def _compute_valid_vehicle_services(self):
        for record in self:
            service_ids = record.vehicle_service_team_ids.mapped('vehicle_service_id').ids
            record.valid_vehicle_service_ids = [(6, 0, service_ids)]

    @api.onchange('product_id')
    def _onchange_spare_part_price(self):
        """Onchange Spare Parts Charges"""
        for rec in self:
            rec.unit_price = rec.product_id.lst_price

    @api.depends('qty', 'unit_price')
    def _compute_sub_total(self):
        """Total Spare Parts Charges"""
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price


class TaskSparePart(models.Model):
    """Task Spare Parts"""
    _name = 'task.spare.parts'
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', domain="[('is_vehicle_part', '=', True)]",
                                 required=True, string='Spare Part')
    vehicle_service_ids = fields.Many2many('vehicle.service', string="Services")
    qty = fields.Integer(string="Quantity", default=1)
    project_task_id = fields.Many2one('project.task', ondelete="cascade")
