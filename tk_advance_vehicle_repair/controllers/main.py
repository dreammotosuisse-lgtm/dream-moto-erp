# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from datetime import datetime
import pytz
from odoo.addons.portal.controllers.portal import CustomerPortal, pager


def validate_mandatory_fields(mandate_fields, kw):
    """ Validate Mandatory Fields """
    error, data = None, {}
    for key, value in mandate_fields.items():
        if not kw.get(key):
            error = "Mandatory fields " + value + " Missing"
            break
        data[key] = kw.get(key)
    return error, data


def validate_optional_fields(opt_fields, kw):
    """ Validate Optional Fields """
    data = {}
    for fld in opt_fields:
        if kw.get(fld):
            data[fld] = kw.get(fld)
    return data


class VehicleBookingWebsite(http.Controller):
    """ Vehicle Booking Website """

    @staticmethod
    def _get_initial_values():
        """ Get Initial Values """
        company = request.env.company
        country = company.country_id

        customer_state = request.env['res.country.state'].sudo().search([
            ('country_id', '=', country.id)
        ]) if country else request.env['res.country.state'].sudo().browse([])

        vehicle_brands = request.env['vehicle.brand'].sudo().search([])
        vehicle_models = request.env['vehicle.model'].sudo().search([])
        vehicle_fuel_types = request.env['vehicle.fuel.type'].sudo().search([])
        register_vehicles = request.env['register.vehicle'].sudo().search(
            [('customer_id', '=', request.env.user.partner_id.id)])
        booking_appointment = request.env['booking.appointment'].sudo().search([])
        website_slot_booking = request.env['ir.config_parameter'].sudo().get_param(
            'tk_advance_vehicle_repair.website_slot_booking')
        return {
            'customer_state': customer_state,
            'vehicle_brands': vehicle_brands,
            'vehicle_models': vehicle_models,
            'vehicle_fuel_types': vehicle_fuel_types,
            'register_vehicles': register_vehicles,
            'booking_appointment': booking_appointment,
            'website_slot_booking': website_slot_booking,
        }

    @http.route('/get_vehicle_model', type='jsonrpc', auth='public')
    def get_vehicle_brand_wise_models(self, vehicle_brand_id):
        """ Get Vehicle Brand wise Models """
        vehicle_model = {}
        if not vehicle_brand_id:
            return vehicle_model
        vehicle_models = request.env['vehicle.model'].sudo().search(
            [('vehicle_brand_id', '=', int(vehicle_brand_id))])
        for data in vehicle_models:
            vehicle_model[data.id] = data.name
        return vehicle_model

    @http.route('/get_booking_day', type='jsonrpc', auth='public')
    def get_booking_day(self, **kw):
        """ Get available booking slots for a given day """
        selected_date_str = kw.get('selected_date')
        if not selected_date_str:
            return {'error': 'No date provided'}

        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        day_name = selected_date.strftime("%A").lower()

        # Fetch appointments configured for that day
        day_appointments = request.env['booking.appointment'].sudo().search([
            ('appointment_day', '=', day_name)
        ])

        if not day_appointments:
            return {'slot_id': [], 'from_time': [], 'to_time': [], 'appointment': []}

        user_tz = request.env.user.tz or 'UTC'
        now_dt = datetime.now(pytz.timezone(user_tz))
        today = now_dt.date()
        now_time_float = now_dt.hour + now_dt.minute / 60.0

        # Collect all slots for the day
        total_slots = day_appointments.mapped('booking_appointment_slot_ids')

        # Find already booked slots for that date
        booked_slots = request.env['vehicle.booking'].sudo().search([
            ('booking_date', '=', selected_date_str),
            ('booking_stages', 'not in', ['draft', 'cancel']),
            ('booking_appointment_slot_id', '!=', False),
        ]).mapped('booking_appointment_slot_id')
        # Remove booked slots
        available_slots = total_slots - booked_slots
        # Today booking filter past slots
        if selected_date == today:
            available_slots = available_slots.filtered(
                lambda slot: slot.from_time > now_time_float)
        return {
            'appointment': booked_slots.ids,
            'slot_id': available_slots.ids,
            'from_time': [slot.from_time for slot in available_slots],
            'to_time': [slot.to_time for slot in available_slots],
        }

    @http.route('/get_registered_vehicles', type='jsonrpc', auth='public')
    def get_vehicle_details(self, register_vehicle_id):
        """ Get Vehicle Details """
        if not register_vehicle_id:
            return False
        vehicle = request.env['register.vehicle'].sudo().browse(int(register_vehicle_id))
        if not vehicle:
            return False
        details = {
            'vehicle_brand_id': vehicle.vehicle_brand_id.id,
            'vehicle_model_id': vehicle.vehicle_model_id.id,
            'vehicle_fuel_type_id': vehicle.vehicle_fuel_type_id.id,
            'registration_no': vehicle.registration_no,
            'transmission_type': vehicle.transmission_type,
            'vin_no': vehicle.vin_no,
        }
        return details

    @http.route('/vehicle/booking', type='http', auth='user', website=True)
    def get_vehicle_booking(self):
        """ Get Vehicle Booking """
        values = self._get_initial_values()
        return request.render('tk_advance_vehicle_repair.vehicle_booking_form', values)

    @http.route('/create/vehicle-booking', type='http', auth='user', website=True)
    def create_web_vehicle_booking(self, **kw):
        """ Create Vehicle Booking """
        values = self._get_initial_values()
        mandatory_fields = {'vehicle_brand_id': 'Vehicle Brand',
                            'vehicle_model_id': 'Vehicle Model',
                            'registration_no': 'Registration No.',
                            'vehicle_fuel_type_id': 'Fuel Type',
                            'city': 'City',
                            }
        optional_fields = ['transmission_type', 'vin_no', 'vehicle_from', 'booking_date',
                           'booking_type', 'phone', 'register_vehicle_id', 'customer_id',
                           'customer_observation', 'phone', 'email', 'street', 'street2',
                           'zip', 'state_id', 'booking_appointment_slot_id']

        error, booking_data = validate_mandatory_fields(mandatory_fields, kw)
        if error:
            values['error'] = error
            kw.update(values)
            return request.render('tk_advance_vehicle_repair.vehicle_booking_form', kw)
        opt_data = validate_optional_fields(optional_fields, kw)
        booking_data.update(opt_data)

        booking_data.update({
            'customer_id': request.env.user.partner_id.id,
            'phone': request.env.user.partner_id.phone,
            'email': request.env.user.partner_id.email,
            'country_id': request.env.company.country_id.id,
            'booking_source': 'website',
        })

        booking_details = request.env['vehicle.booking'].sudo().create(booking_data)
        return request.render('tk_advance_vehicle_repair.repair_order_created',
                              {'booking_details': booking_details})

    @http.route(
        ['/booking/vehicle-booking-details', '/booking/vehicle-booking-details/page/<int:page>'],
        type='http', auth='public', website=True)
    def get_vehicle_booking_list(self, page=1):
        """Display paginated vehicle booking requests for the logged-in customer."""
        page_size = 10
        offset = (page - 1) * page_size
        partner_id = request.env.user.partner_id.id

        vehicle_booking = request.env['vehicle.booking'].sudo()

        total_bookings = vehicle_booking.search_count([
            ('customer_id', '=', partner_id),
            ('booking_source', '=', 'website')
        ])
        booking_requests = vehicle_booking.search(
            [('customer_id', '=', partner_id), ('booking_source', '=', 'website')],
            limit=page_size,
            offset=offset,
            order='booking_number desc'
        )
        pager_details = pager(
            url="/booking/vehicle-booking-details",
            total=total_bookings,
            page=page,
            step=page_size,
            scope=5
        )
        return request.render('tk_advance_vehicle_repair.vehicle_booking_view', {
            'booking_requests': booking_requests,
            'page_name': 'booking_request_tree',
            'pager': pager_details,
        })

    @http.route("/booking/request-information/<string:access_token>", type='http', auth="user",
                website=True)
    def booking_request_information_detail(self, access_token):
        """Booking request information"""
        # Ensure the current user is the customer who made the booking
        bookings = request.env['vehicle.booking'].sudo().search(
            [('access_token', '=', access_token),
             ('customer_id', '=', request.env.user.partner_id.id)], limit=1)
        if not bookings:
            return request.redirect('/')
        # Get all bookings for the logged-in user
        user_bookings = request.env['vehicle.booking'].sudo().search([
            ('customer_id', '=', request.env.user.partner_id.id)])
        bookings_ids = user_bookings.ids
        current_index = bookings_ids.index(
            bookings.id) if bookings.id in bookings_ids else -1
        if current_index == -1:
            return request.redirect('/')
        # Previous and Next URLs
        prev_url = f"/booking/request-information/{user_bookings[current_index - 1].access_token}" \
            if current_index > 0 else None
        next_url = f"/booking/request-information/{user_bookings[current_index + 1].access_token}" \
            if current_index < len(bookings_ids) - 1 else None
        return request.render('tk_advance_vehicle_repair.vehicle_booking_details', {
            'vehicle_bookings': bookings,
            'page_name': 'booking_request_form',
            'prev_record': prev_url,
            'next_record': next_url,
        })


class VehicleBookingPortal(CustomerPortal):
    """ Vehicle Booking Portal """

    def _prepare_home_portal_values(self, counters):
        """Prepare portal values including vehicle booking count."""
        # Call the parent method to get the base values
        values = super(VehicleBookingPortal, self)._prepare_home_portal_values(counters)
        # Calculate the booking count for the logged-in customer
        count = request.env['vehicle.booking'].sudo().search_count([
            ('customer_id', '=', request.env.user.partner_id.id),
            ('booking_source', '=', 'website'),
        ])
        if counters:
            values['count'] = count
        return values
