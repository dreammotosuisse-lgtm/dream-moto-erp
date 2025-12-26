import logging
from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)
logging.getLogger('odoo.addons.mail').setLevel(logging.ERROR)


@tagged('enterprise_related', "advance_vehicle_repair")
class VehicleRepairData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Mail = cls.env['mail.mail'].with_context(test_mode=True)
        cls.product = cls.env["product.product"].create({
        "name": "Product One", "type": "service", 
        "lst_price": 10})
        cls.product_two = cls.env["product.product"].create({
        "name": "Product Two", "type": "service", 
        "lst_price": 20})
        cls.company = cls.env.ref("base.main_company")
        cls.customer = cls.env["res.partner"].create({
            "name": "Customer", "email": "customer@gmail.com",
            "street": "Street One", "street2": "Street Two",
            "city": "City", "country_id": 104, "state_id": 12,
            "zip": "305013", "phone": "1234567890", })
        cls.user = cls.env["res.users"].create({
            "name":"User One", "login": "U1"})
        cls.journal_bank = cls.env["account.journal"].search(
            [("type", "=", "bank")], limit=1)
        cls.company_currency = cls.env.company.currency_id
        cls.tax = cls.env["account.tax"].create({
            "name": "10% incl", "type_tax_use": "sale", "amount_type":
            "percent", "amount": 10.0, })
        cls.currency = cls.env["res.currency"].search([("name", "=", "USD")],
                                                      limit=1)
        cls.vehicle_brand = cls.env["vehicle.brand"].create({
            "name": "VB", })
        cls.vehicle_model = cls.env["vehicle.model"].create({
            "name": "VM", "vehicle_brand_id": cls.vehicle_brand.id})
        cls.fuel_type = cls.env["vehicle.fuel.type"].create({
            "name": "Fuel"})
        cls.part_exterior = cls._create_vehicle_parts_info({
            "name": "Part Exterior", "type": "exterior"})
        cls.part_interior = cls._create_vehicle_parts_info({
            "name": "Part Interior", "type": "interior"})
        cls.part_under_hood = cls._create_vehicle_parts_info({
            "name": "Part Under Hood", "type": "under_hood"})
        cls.part_under_vehicle = cls._create_vehicle_parts_info({
            "name": "Part Under Vehicle", "type": "under_vehicle"})
        cls.part_fluids = cls._create_vehicle_parts_info({
            "name": "Part Fluids", "type": "fluids"})
        cls.part_tires = cls._create_vehicle_parts_info({
            "name": "Part Tires", "type": "tires"})
        cls.part_brake_condition = cls._create_vehicle_parts_info({
            "name": "Part Brake Condition", "type": "brake_condition"})
        cls.vehicle_location = cls.env["vehicle.condition.location"].create({
            "location": "Location"})
        cls.vehicle_condition = cls.env["vehicle.condition"].create({
            "condition": "VC", "condition_code": "CC"})
        cls.item_mechanical = cls.env["vehicle.item"].create({
            "name": "Item Mechanical", "item_category": "mechanical"})
        cls.item_interior = cls.env["vehicle.item"].create({
            "name": "Item Interior", "item_category": "interior"})
        cls.component_bottom_side = cls.env["vehicle.component"].create({
            "name": "Bottom Side", "compo_vehicle_side": "bottom_side"})
        cls.component_top_side = cls.env["vehicle.component"].create({
            "name": "Top Side", "compo_vehicle_side": "top_side"})
        cls.fluids_bottom_side = cls.env["vehicle.fluid"].create({
            "name": "Bottom Side", "fluid_vehicle_side": "bottom_side"})
        cls.fluids_top_side = cls.env["vehicle.fluid"].create({
            "name": "Top Side", "fluid_vehicle_side": "top_side"})
        cls.checklist_template = cls._create_checklist_template({
            "name": "CT One", })
        cls.checklist_template_item_one = cls._create_checklist_template_item({
            "name": "CTI 1", "checklist_template_id": cls.checklist_template.id})

        cls.checklist_template_item_two = cls._create_checklist_template_item({
            "name": "CTI 2", "checklist_template_id": cls.checklist_template.id})

        cls.checklist_template_item_three = cls._create_checklist_template_item({
            "name": "CTI 3", "checklist_template_id": cls.checklist_template.id})

        cls.checklist_template_item_four = cls._create_checklist_template_item({
            "name": "CTI 4", "checklist_template_id": cls.checklist_template.id})

        cls.checklist_template_item_five = cls._create_checklist_template_item({
            "name": "CTI 5", "checklist_template_id": cls.checklist_template.id})
        
        cls.register_vehicle = cls.env["register.vehicle"].create({
            "customer_id": cls.customer.id, "vehicle_brand_id": 
            cls.vehicle_brand.id, "vehicle_model_id": cls.vehicle_model.id,
            "registration_no": "1234567890", "vehicle_fuel_type_id": 
            cls.fuel_type.id, "transmission_type": "automatic", "vin_no": 
            "123456789",})
        
        cls.vehicle_service_one = cls._create_vehicle_service({
            "service_name": "S1", "service_charge": 10, "product_id":
            cls.product.id, })
        cls.vehicle_service_two = cls._create_vehicle_service({
            "service_name": "S2", "service_charge": 20, "product_id":
            cls.product.id, })


    @classmethod
    def _create_vehicle_parts_info(cls, data: dict):
        return cls.env["vehicle.part.info"].create(data)

    @classmethod
    def _create_booking(cls, data: dict):
        return cls.env["vehicle.booking"].create(data)

    @classmethod
    def _create_inspection_job_card(cls, data: dict):
        return cls.env["inspection.job.card"].create(data)

    @classmethod
    def _create_checklist_template_item(cls, data: dict):
        return cls.env["checklist.template.item"].create(data)

    @classmethod
    def _create_checklist_template(cls, data: dict):
        return cls.env["checklist.template"].create(data)

    @classmethod
    def _create_inspection_checklist(cls, data: dict):
        return cls.env["inspection.checklist"].create(data)
    
    @classmethod
    def _create_inspection_repair_team(cls, data: dict):
        return cls.env["inspection.repair.team"].create(data) 
    
    @classmethod
    def _create_vehicle_service(cls, data: dict):
        return cls.env["vehicle.service"].create(data)
    
    @classmethod
    def _create_vehicle_spare_part(cls, data: dict):
        return cls.env["vehicle.spare.part"].create(data)
    
    @classmethod
    def _create_repair_job_card(cls, data: dict):
        return cls.env["repair.job.card"].create(data)
    
    @classmethod
    def _create_vehicle_service_team(cls, data: dict):
        return cls.env["vehicle.service.team"].create(data)
    
    @classmethod
    def _create_repair_checklist(cls, data: dict):
        return cls.env["repair.checklist"].create(data)
    
    @classmethod
    def _create_vehicle_order_spare_part(cls, data: dict):
        return cls.env["vehicle.order.spare.part"].create(data)