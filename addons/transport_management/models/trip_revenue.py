# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransportTripRevenue(models.Model):
    _name = 'transport.trip.revenue'
    _description = 'Trip Revenue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    trip_id = fields.Many2one(
        'transport.trip',
        string='Trip',
        required=True,
        ondelete='cascade'
    )
    
    name = fields.Char(string='Description', required=True)
    
    revenue_type = fields.Selection([
        ('cargo_transport', 'Cargo Transport'),
        ('passenger_transport', 'Passenger Transport'),
        ('extra_service', 'Extra Service'),
        ('insurance_coverage', 'Insurance Coverage'),
        ('other', 'Other'),
    ], string='Revenue Type', required=True)
    
    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today
    )
    
    customer = fields.Char(string='Customer')
    
    invoice_number = fields.Char(string='Invoice Number')
    
    payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], string='Payment Status', default='not_paid')
    
    payment_date = fields.Date(string='Payment Date')
    
    notes = fields.Text(string='Notes')
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    @api.onchange('revenue_type')
    def _onchange_revenue_type(self):
        if self.revenue_type:
            revenue_names = {
                'cargo_transport': 'Cargo Transport Fee',
                'passenger_transport': 'Passenger Transport Fee',
                'extra_service': 'Extra Service Fee',
                'insurance_coverage': 'Insurance Coverage Fee',
                'other': 'Other Revenue',
            }
            self.name = revenue_names.get(self.revenue_type, 'Revenue')
