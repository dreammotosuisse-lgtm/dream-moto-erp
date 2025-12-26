# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class SaleOrder(models.Model):
    """Sale Order"""
    _inherit = 'sale.order'
    _description = __doc__

    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card")
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")

    def _prepare_invoice(self):
        """Prepare the dictionary of values to create the invoice."""
        res = super(SaleOrder, self)._prepare_invoice()
        if self.inspection_job_card_id:
            res['inspection_job_card_id'] = self.inspection_job_card_id.id
        if self.repair_job_card_id:
            res['repair_job_card_id'] = self.repair_job_card_id.id
        return res


class SaleInvoice(models.Model):
    """Sale Invoice"""
    _inherit = 'account.move'
    _description = __doc__

    inspection_job_card_id = fields.Many2one('inspection.job.card', string="Inspection Job Card")
    repair_job_card_id = fields.Many2one('repair.job.card', string="Repair Job Card")
