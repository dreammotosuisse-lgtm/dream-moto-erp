# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class VehicleService(models.Model):
    """Vehicle Service"""
    _name = 'vehicle.service'
    _inherits = {'product.product': 'product_id'}
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(related="product_id.name", store=True, readonly=False, required=True,
                       inherited=True, translate=False)
    service_name = fields.Char(string=" Name", translate=True, compute="_compute_service_name",
                               store=True)
    product_id = fields.Many2one('product.product', required=True, ondelete='cascade',
                                 index=True, string=' Product')
    type = fields.Selection(related="product_id.type", default='service',
                                     readonly=False, store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")

    @api.depends('product_id', 'name')
    def _compute_service_name(self):
        """Compute service name"""
        for rec in self:
            rec.service_name = rec.product_id.name or rec.name or ''

    # DEPRECATED
    service_charge = fields.Monetary()


class ServiceTeam(models.Model):
    """Service Team"""
    _name = 'service.team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'title'

    color = fields.Integer()
    title = fields.Char(translate=True)
    service_manager_id = fields.Many2one(
        'res.users', string="Responsible", default=lambda self: self.env.user,
        domain=lambda self: [('all_group_ids', 'in', [self.env.ref('base.group_user').id])])
    team_member_ids = fields.Many2many(
        'res.users', string="Team Members",
        domain=lambda self: [('all_group_ids', 'in', [self.env.ref('base.group_user').id])])
    service_team_project_id = fields.Many2one('project.project', store=True, string="Project",
                                              ondelete='cascade')

    @api.model_create_multi
    def create(self, vals_list):
        """ Create Method """
        res = super().create(vals_list)
        for rec in res:
            project_id = self.env['project.project'].sudo().create({
                'name': rec.title,
                'user_id': self.env.user.id,
                'company_id': self.env.company.id,
            })
            rec.service_team_project_id = project_id.id
        return res

    @api.constrains('team_member_ids')
    def _check_team_members(self):
        """Ensure at least one team member is added."""
        for record in self:
            if not record.team_member_ids:
                raise ValidationError(_("Please add at least one team member to the team."))


class VehicleServiceTeam(models.Model):
    """Vehicle Service Team"""
    _name = 'vehicle.service.team'
    _description = __doc__
    _rec_name = 'vehicle_service_id'

    vehicle_service_id = fields.Many2one('vehicle.service', string="Service", required=True)
    service_team_id = fields.Many2one('service.team', string="Team")
    member_ids = fields.Many2many(related="service_team_id.team_member_ids")
    vehicle_service_team_members_ids = fields.Many2many('res.users', string="Members",
                                                        domain="[('id', 'in', member_ids)]")

    start_date = fields.Date(default=fields.Date.today())
    end_date = fields.Date()
    team_project_id = fields.Many2one(related="service_team_id.service_team_project_id",
                                      string="Project")
    team_task_id = fields.Many2one('project.task')
    work_is_done = fields.Boolean(related='team_task_id.work_is_done',
                                  string="Work is Done")
    service_charge = fields.Monetary()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    repair_job_card_id = fields.Many2one('repair.job.card', ondelete="cascade")

    @api.onchange('vehicle_service_id')
    def _onchange_service_charge(self):
        """Vehicle Service Charge"""
        for rec in self:
            rec.service_charge = rec.vehicle_service_id.lst_price

    @api.onchange('service_team_id')
    def _onchange_service_team_id(self):
        """Onchange service team"""
        self.vehicle_service_team_members_ids = False

    def create_service_task(self):
        """Create a Service Task"""
        self.ensure_one()
        service_name = self.vehicle_service_id.name or ''
        team_name = self.service_team_id.title or ''
        # Create the service task.
        team_members = []
        if self.vehicle_service_team_members_ids:
            team_members = self.vehicle_service_team_members_ids.ids
        service_task = self.env['project.task'].sudo().create({
            'name': f"{service_name} Assigned to {team_name}",
            'project_id': self.team_project_id.id,
            'vehicle_service_id': self.vehicle_service_id.id,
            'partner_id': self.repair_job_card_id.customer_id.id,
            'user_ids': [(6, 0, team_members)],
            'date_assign': self.start_date,
            'date_deadline': self.end_date,
            'repair_job_card_id': self.repair_job_card_id.id,
        })
        # Link the created task to the current record.
        self.team_task_id = service_task.id
        # Prepare spare parts data for the created task.
        spare_parts_data = [{
            'product_id': part.product_id.id,
            'vehicle_service_ids': [(6, 0, part.vehicle_service_ids.ids)],
            'qty': part.qty,
            'project_task_id': service_task.id,
        } for part in self.repair_job_card_id.vehicle_order_spare_part_ids]
        # Create spare parts records
        if spare_parts_data:
            self.env['task.spare.parts'].create(spare_parts_data)

    @api.onchange('work_is_done')
    def _onchange_team_work_status(self):
        """Team Work Status"""
        for record in self:
            service_team_id = False
            if record.work_is_done:
                service_team_id = record.service_team_id
            record.service_team_id = service_team_id

    @api.constrains('start_date', 'end_date')
    def _contract_check_dates(self):
        """Check Start and End Date"""
        for record in self:
            if record.end_date and record.start_date and record.start_date > record.end_date:
                raise ValidationError(_("Kindly verify that the vehicle services end date occurs "
                                        "after the start date"))

    @api.ondelete(at_uninstall=False)
    def _unlink_service_record(self):
        """Unlink Service Record"""
        if any(record.team_task_id for record in self):
            raise ValidationError(_('You cannot delete records with created team tasks.'))


class InspectionRepairTeam(models.Model):
    """Inspection Repair Team"""
    _name = 'inspection.repair.team'
    _description = __doc__
    _rec_name = 'vehicle_service_id'

    vehicle_service_id = fields.Many2one('vehicle.service', string="Service", required=True)
    start_date = fields.Date(default=fields.Date.today())
    end_date = fields.Date()
    service_charge = fields.Monetary()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related="company_id.currency_id")
    inspection_job_card_id = fields.Many2one('inspection.job.card', ondelete="cascade")

    # unused
    service_team_id = fields.Many2one('service.team', string="Team")
    member_ids = fields.Many2many(related="service_team_id.team_member_ids")
    vehicle_service_team_members_ids = fields.Many2many('res.users', string="Members",
                                                        domain="[('id', 'in', member_ids)]")
    work_is_done = fields.Boolean(related='team_task_id.work_is_done', string="Work is Done")
    team_project_id = fields.Many2one(related="service_team_id.service_team_project_id",
                                      string="Project")
    team_task_id = fields.Many2one('project.task', readonly=True, store=True)

    @api.onchange('vehicle_service_id')
    def _onchange_service_charge(self):
        """Vehicle Service Charge"""
        for rec in self:
            rec.service_charge = rec.vehicle_service_id.lst_price

    # DEPRECATED
    def create_service_task(self):
        """ Create Service Task """
        service_id = self.env['project.task'].sudo().create({
            'name': self.vehicle_service_id.name,
            'project_id': self.team_project_id.id,
            'vehicle_service_id': self.vehicle_service_id.id,
            'partner_id': self.inspection_job_card_id.customer_id.id,
            'date_assign': self.start_date,
            'date_deadline': self.end_date,
            'inspection_job_card_id': self.inspection_job_card_id.id
        })
        self.team_task_id = service_id.id
