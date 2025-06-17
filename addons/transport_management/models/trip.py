# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportTrip(models.Model):
    _name = 'transport.trip'
    _description = 'Transport Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'departure_date desc'

    name = fields.Char(
        string='Trip Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    # Basic Trip Information
    departure_location = fields.Selection([
        ('morocco', 'Morocco'),
        ('france', 'France'),
    ], string='Departure', required=True, tracking=True)
    
    destination_location = fields.Selection([
        ('morocco', 'Morocco'),
        ('france', 'France'),
    ], string='Destination', required=True, tracking=True)
    
    departure_city = fields.Char(string='Departure City', required=True)
    destination_city = fields.Char(string='Destination City', required=True)
    
    trip_type = fields.Selection([
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    ], string='Trip Type', required=True, default='one_way', tracking=True)
    
    departure_date = fields.Datetime(
        string='Departure Date',
        required=True,
        tracking=True
    )
    
    arrival_date = fields.Datetime(
        string='Expected Arrival Date',
        tracking=True
    )
    
    actual_arrival_date = fields.Datetime(
        string='Actual Arrival Date',
        tracking=True
    )
    
    return_date = fields.Datetime(
        string='Return Date',
        help="For round trips only"
    )
    
    # Vehicle and Driver Assignment
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        tracking=True
    )
    
    driver_id = fields.Many2one(
        'hr.employee',
        string='Main Driver',
        domain=[('is_driver', '=', True)],
        required=True,
        tracking=True
    )
    
    co_driver_id = fields.Many2one(
        'hr.employee',
        string='Co-Driver',
        domain=[('is_driver', '=', True)],
        tracking=True
    )
    
    # Trip Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Service Information
    service_type = fields.Selection([
        ('cargo', 'Cargo Transport'),
        ('passenger', 'Passenger Transport'),
        ('mixed', 'Mixed'),
    ], string='Service Type', required=True)
    
    cargo_description = fields.Text(string='Cargo Description')
    cargo_weight = fields.Float(string='Cargo Weight (kg)')
    passenger_count = fields.Integer(string='Number of Passengers')
    
    # Financial Information
    revenue_ids = fields.One2many(
        'transport.trip.revenue',
        'trip_id',
        string='Revenues'
    )
    
    expense_ids = fields.One2many(
        'transport.trip.expense',
        'trip_id',
        string='Expenses'
    )
    
    total_revenue = fields.Monetary(
        string='Total Revenue',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    
    total_expenses = fields.Monetary(
        string='Total Expenses',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    
    profit = fields.Monetary(
        string='Profit',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_totals',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Additional Information
    notes = fields.Text(string='Notes')
    distance_km = fields.Float(string='Distance (km)')
    fuel_consumption = fields.Float(string='Fuel Consumption (L)')
    
    # Computed fields for dashboard
    duration_days = fields.Float(
        string='Duration (Days)',
        compute='_compute_duration'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('transport.trip') or _('New')
        return super(TransportTrip, self).create(vals)

    @api.depends('revenue_ids.amount', 'expense_ids.amount')
    def _compute_totals(self):
        for trip in self:
            trip.total_revenue = sum(trip.revenue_ids.mapped('amount'))
            trip.total_expenses = sum(trip.expense_ids.mapped('amount'))
            trip.profit = trip.total_revenue - trip.total_expenses
            if trip.total_revenue:
                trip.profit_margin = (trip.profit / trip.total_revenue) * 100
            else:
                trip.profit_margin = 0.0

    @api.depends('departure_date', 'actual_arrival_date', 'arrival_date')
    def _compute_duration(self):
        for trip in self:
            if trip.departure_date:
                end_date = trip.actual_arrival_date or trip.arrival_date
                if end_date:
                    delta = end_date - trip.departure_date
                    trip.duration_days = delta.days + (delta.seconds / 86400.0)
                else:
                    trip.duration_days = 0.0
            else:
                trip.duration_days = 0.0

    @api.constrains('departure_location', 'destination_location')
    def _check_locations(self):
        for trip in self:
            if trip.departure_location == trip.destination_location:
                raise ValidationError(_("Departure and destination locations must be different."))

    @api.constrains('departure_date', 'arrival_date')
    def _check_dates(self):
        for trip in self:
            if trip.departure_date and trip.arrival_date:
                if trip.departure_date >= trip.arrival_date:
                    raise ValidationError(_("Arrival date must be after departure date."))

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        self.message_post(body=_("Trip confirmed"))

    def action_start(self):
        self.write({'state': 'in_progress'})
        self.message_post(body=_("Trip started"))

    def action_deliver(self):
        self.write({'state': 'delivered'})
        self.message_post(body=_("Trip delivered"))

    def action_return(self):
        if self.trip_type == 'round_trip':
            self.write({'state': 'returned'})
            self.message_post(body=_("Trip returned"))
        else:
            self.action_done()

    def action_done(self):
        self.write({'state': 'done'})
        self.message_post(body=_("Trip completed"))

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        self.message_post(body=_("Trip cancelled"))

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        self.message_post(body=_("Trip reset to draft"))

    def action_view_expenses(self):
        action = self.env.ref('transport_management.action_transport_trip_expense').read()[0]
        action['domain'] = [('trip_id', '=', self.id)]
        action['context'] = {
            'default_trip_id': self.id,
            'search_default_trip_id': self.id,
        }
        return action

    def action_view_revenues(self):
        action = self.env.ref('transport_management.action_transport_trip_revenue').read()[0]
        action['domain'] = [('trip_id', '=', self.id)]
        action['context'] = {
            'default_trip_id': self.id,
            'search_default_trip_id': self.id,
        }
        return action

    def name_get(self):
        result = []
        for trip in self:
            name = f"{trip.name} - {trip.departure_city} → {trip.destination_city}"
            result.append((trip.id, name))
        return result
