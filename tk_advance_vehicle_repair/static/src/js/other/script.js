/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";

// vehicle brand wise model
$("#vehicle_brand_id").on("change", function () {
    var text = "<option value='' selected='selected'>Select Model</option>";
    var brandId = $(this).val();
    rpc("/get_vehicle_model", {
        vehicle_brand_id: brandId
    }).then(function (vehicle_model) {
        if (vehicle_model) {
            for (var key in vehicle_model) {
                text += '<option value="' + key + '">' + vehicle_model[key] + '</option>';
            }
            $('#vehicle_model_id').empty().append(text);
        }
    });
});

// select register vehicle
$('#register_vehicle_id').change(function () {
    var regVehicleId = $('#register_vehicle_id').val();
    rpc("/get_registered_vehicles", {
        'register_vehicle_id': regVehicleId
    }).then(function (result) {
        // Check if result is available
        if (result) {
            $('#vehicle_brand_id').val(result.vehicle_brand_id || '');
            $('#vehicle_model_id').val(result.vehicle_model_id || '');
            $('#vehicle_fuel_type_id').val(result.vehicle_fuel_type_id || '');
            $('#vin_no').val(result.vin_no || '');
            $('#registration_no').val(result.registration_no || '');
            $('.transmission_type').val(result.transmission_type || '');

            if (result.transmission_type === 'manual') {
                $('#manual').prop('checked', true);
                $('#automatic').prop('checked', false);
                $('#cvt').prop('checked', false);
            } else if (result.transmission_type === 'automatic') {
                $('#automatic').prop('checked', true);
                $('#manual').prop('checked', false);
                $('#cvt').prop('checked', false);
            } else {
                $('#cvt').prop('checked', true);
                $('#automatic').prop('checked', false);
                $('#manual').prop('checked', false);
            }
        } else {
            resetFields();
        }
    });
});

// Reset all fields to empty
function resetFields() {
    $('#vehicle_brand_id, #vehicle_model_id, #vehicle_fuel_type_id, #registration_no, #vin_no, .transmission_type').val('');
    $('#manual, #automatic, #cvt').prop('checked', false);
}

// fleet from onchange
$("#new").on("change", function () {
    resetFields();
    $('#from_fleet_vehicle, #from_customer_vehicle').addClass('d-none');
});

$("#customer_vehicle").on("change", function () {
    resetFields();
    $('#from_fleet_vehicle').addClass('d-none');
    $('#from_customer_vehicle').removeClass('d-none');
});

$("#vehicle_brand_id").on("change", function () {
    $('#vehicle_fuel_type_id').val('');
});


// Select Slot
function convertToTime(e) {
    const floatTime = e;
    const hours = Math.floor(floatTime);
    const minutes = (floatTime - hours) * 60;
    const formattedTime = `${hours.toString().padStart(2, '0')}:${Math.round(minutes).toString().padStart(2, '0')}`;
    return formattedTime
}


// Select Booking Date
$('#booking_date').on("change", function () {
    $('#booking_appointment_slot_id').empty();
    let text = '<option selected="selected" value="">Select Slot</option>';

    let selectedDate = $("#booking_date").val();
    let currentDate = new Date(selectedDate);
    currentDate.setHours(0, 0, 0, 0); // Reset time to start of the day

    let todayDate = new Date();
    todayDate.setHours(0, 0, 0, 0); // Reset time to start of the day

    if (currentDate >= todayDate) {
        $('#alert').addClass('d-none').text("");
        $('#booking_slot_main').removeClass('d-none');
        $('#submit_button').removeClass('d-none');

        rpc('/get_booking_day', {
            'selected_date': selectedDate
        }).then(function (result) {
            if (result['from_time'][0]) {
                // Slots are available
                $('#alert').addClass('d-none').text("");
                $('#booking_slot_main').removeClass('d-none');

                result['from_time'].forEach((e, i) => {
                    let first_time = convertToTime(e);
                    let second_time = convertToTime(result['to_time'][i]);
                    text += `<option class="dynamic_slot" value="${result['slot_id'][i]}">
                                ${first_time} - ${second_time}
                            </option>`;
                });
                $('#booking_appointment_slot_id').append(text);
            } else {
                // No slots available for the selected date
                $('#alert').removeClass('d-none').text("Slot not available");
                $('#booking_slot_main').addClass('d-none');
            }
        });
    } else {
        // Invalid date: Show alert, hide booking slots
        $('#alert').removeClass('d-none').text("Selected date cannot be in the past.");
        $('#booking_slot_main').addClass('d-none');
        $('#submit_button').addClass('d-none');
    }
});