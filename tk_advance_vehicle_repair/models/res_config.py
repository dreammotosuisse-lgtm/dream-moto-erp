# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class VehicleConfigSetting(models.TransientModel):
    """Vehicle Config Setting"""
    _inherit = 'res.config.settings'
    _description = __doc__

    website_slot_booking = fields.Boolean(
        config_parameter='tk_advance_vehicle_repair.website_slot_booking')
