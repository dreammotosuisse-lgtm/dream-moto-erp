# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ScratchReport(models.Model):
    """Scratch Report"""
    _name = 'scratch.report'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(translate=True)
    avatar = fields.Binary()
    vehicle_brand_id = fields.Many2one('vehicle.brand', string="Brand")
