# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class BookingAppointment(models.Model):
    """Booking Appointment"""
    _name = 'booking.appointment'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(translate=True)
    appointment_day = fields.Selection([
        ('monday', "Monday"),
        ('tuesday', "Tuesday"),
        ('wednesday', "Wednesday"),
        ('thursday', "Thursday"),
        ('friday', "Friday"),
        ('saturday', "Saturday"),
        ('sunday', "Sunday")])
    booking_appointment_slot_ids = fields.One2many(comodel_name='booking.appointment.slot',
                                                   inverse_name='booking_appointment_id')


class BookingAppointmentSlot(models.Model):
    """Booking Appointment Slot"""
    _name = 'booking.appointment.slot'
    _description = __doc__
    _rec_name = 'title'

    title = fields.Char(translate=True)
    from_time = fields.Float(string="Starting Time")
    to_time = fields.Float(string="Closing Time")
    booking_appointment_id = fields.Many2one('booking.appointment', string="Booking Appointment",
                                             ondelete='cascade')

    @api.model_create_multi
    def create(self, vals_list):
        """Create booking appointment slot"""
        for vals in vals_list:
            self._check_duplicate_slot(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Write booking appointment slot record"""
        if any(field in vals for field in ['title', 'from_time', 'to_time']):
            for record in self:
                updated_vals = {
                    'title': vals.get('title', record.title),
                    'from_time': vals.get('from_time', record.from_time),
                    'to_time': vals.get('to_time', record.to_time),
                }
                self._check_duplicate_slot(updated_vals, exclude_id=record.id)
        return super().write(vals)

    def _check_duplicate_slot(self, vals, exclude_id=False):
        """Check duplicate slots."""
        title = vals.get('title')
        from_time = vals.get('from_time')
        to_time = vals.get('to_time')

        if title and from_time and to_time:
            from_time = round(from_time, 2)
            to_time = round(to_time, 2)
            domain = [
                ('title', '=', title),
                ('from_time', '=', from_time),
                ('to_time', '=', to_time),
            ]
            if exclude_id:
                domain.append(('id', '!=', exclude_id))

            existing_record = self.search(domain, limit=1)
            if existing_record:
                raise ValidationError(
                    _("Appointment slot '{}' starting time {} to {} is already in use. "
                      "Please choose a different time or title.").format(title, from_time, to_time))

    @api.constrains('from_time', 'to_time')
    def _check_time_range(self):
        """Check time range"""
        for record in self:
            if not 0 <= record.from_time <= 24:
                raise ValidationError(_("Starting Time must be between 0 and 24."))
            if not 0 <= record.to_time <= 24:
                raise ValidationError(_("Closing Time must be between 0 and 24."))
            if record.to_time < record.from_time:
                raise ValidationError(_("Closing Time cannot be less than Starting Time."))
            if record.to_time == record.from_time:
                raise ValidationError(_("Starting Time and Closing Time cannot be the same."))
