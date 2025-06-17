# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Driver specific fields
    is_driver = fields.Boolean(string='Is Driver', default=False)
    
    driver_license_number = fields.Char(string='Driver License Number')
    driver_license_category = fields.Selection([
        ('b', 'Category B (Car)'),
        ('c', 'Category C (Truck)'),
        ('d', 'Category D (Bus)'),
        ('ce', 'Category C+E (Truck with Trailer)'),
        ('de', 'Category D+E (Bus with Trailer)'),
    ], string='License Category')
    
    driver_license_expiry = fields.Date(string='License Expiry Date')
    international_license_expiry = fields.Date(string='International License Expiry')
    
    # Professional qualifications
    professional_card_number = fields.Char(string='Professional Card Number')
    professional_card_expiry = fields.Date(string='Professional Card Expiry')
    
    # Experience
    driving_experience_years = fields.Integer(string='Driving Experience (Years)')
    international_routes_experience = fields.Boolean(
        string='International Routes Experience',
        default=False
    )
    
    # Trip tracking
    trip_ids = fields.One2many(
        'transport.trip',
        'driver_id',
        string='Trips as Main Driver'
    )
    
    co_driver_trip_ids = fields.One2many(
        'transport.trip',
        'co_driver_id',
        string='Trips as Co-Driver'
    )
    
    total_trips = fields.Integer(
        string='Total Trips',
        compute='_compute_driver_stats'
    )
    
    total_km_driven = fields.Float(
        string='Total KM Driven',
        compute='_compute_driver_stats'
    )
    
    # Availability
    available_for_trip = fields.Boolean(
        string='Available for Trip',
        default=True
    )
    
    current_location = fields.Selection([
        ('morocco', 'Morocco'),
        ('france', 'France'),
        ('in_transit', 'In Transit'),
    ], string='Current Location')

    @api.depends('trip_ids', 'co_driver_trip_ids')
    def _compute_driver_stats(self):
        for employee in self:
            if employee.is_driver:
                all_trips = employee.trip_ids + employee.co_driver_trip_ids
                employee.total_trips = len(all_trips)
                employee.total_km_driven = sum(all_trips.mapped('distance_km'))
            else:
                employee.total_trips = 0
                employee.total_km_driven = 0.0

    def action_view_trips(self):
        action = self.env.ref('transport_management.action_transport_trip').read()[0]
        action['domain'] = [
            '|',
            ('driver_id', '=', self.id),
            ('co_driver_id', '=', self.id)
        ]
        action['context'] = {
            'default_driver_id': self.id,
        }
        return action

    @api.model
    def _get_drivers_with_expiring_documents(self, days=30):
        """Get drivers with documents expiring in the next X days"""
        today = fields.Date.today()
        future_date = today + timedelta(days=days)
        
        drivers = self.search([
            ('is_driver', '=', True),
            '|', '|',
            ('driver_license_expiry', '<=', future_date),
            ('international_license_expiry', '<=', future_date),
            ('professional_card_expiry', '<=', future_date),
        ])
        return drivers

    @api.model
    def get_available_drivers(self, location=None):
        """Get available drivers, optionally filtered by location"""
        domain = [
            ('is_driver', '=', True),
            ('available_for_trip', '=', True),
        ]
        if location:
            domain.append(('current_location', '=', location))
        
        return self.search(domain)
