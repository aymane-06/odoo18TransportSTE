# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Transport Service Fields
    is_transport_service = fields.Boolean(
        string='Is Transport Service', 
        default=False,
        help="Check if this sale order is for transport services"
    )
    
    trip_id = fields.Many2one(
        'transport.trip', 
        string='Related Trip',
        domain=[('state', 'in', ['planned', 'in_progress'])],
        help="Trip associated with this transport service"
    )
    
    departure_location = fields.Char(
        string='Departure Location',
        default='Morocco'
    )
    
    destination_location = fields.Char(
        string='Destination Location', 
        default='France'
    )
    
    departure_date = fields.Date(string='Departure Date')
    
    return_date = fields.Date(string='Return Date')
    
    trip_type = fields.Selection([
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip')
    ], string='Trip Type', default='one_way')
    
    transport_revenue_ids = fields.One2many(
        'transport.trip.revenue', 
        'sale_order_id', 
        string='Generated Revenues',
        readonly=True
    )
    
    transport_revenue_count = fields.Integer(
        string='Revenue Count',
        compute='_compute_transport_revenue_count'
    )
    
    @api.depends('transport_revenue_ids')
    def _compute_transport_revenue_count(self):
        for order in self:
            order.transport_revenue_count = len(order.transport_revenue_ids)
    
    @api.onchange('is_transport_service')
    def _onchange_is_transport_service(self):
        """Set default transport products when transport service is selected"""
        if self.is_transport_service:
            # Clear existing lines
            self.order_line = [(5, 0, 0)]
            
            # Add default transport service product if exists
            transport_product = self.env['product.product'].search([
                ('name', 'ilike', 'transport'),
                ('type', '=', 'service')
            ], limit=1)
            
            if transport_product:
                self.order_line = [(0, 0, {
                    'product_id': transport_product.id,
                    'product_uom_qty': 1,
                })]
    
    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        """Update locations and dates based on selected trip"""
        if self.trip_id:
            self.departure_location = self.trip_id.departure_location or 'Morocco'
            self.destination_location = self.trip_id.destination_location or 'France'
            self.departure_date = self.trip_id.departure_date
            self.return_date = self.trip_id.return_date
    
    def action_confirm(self):
        """Override to create trip revenue when sale order is confirmed"""
        result = super(SaleOrder, self).action_confirm()
        
        for order in self:
            if order.is_transport_service and not order.transport_revenue_ids:
                # Create trip revenue automatically
                revenue_vals = {
                    'name': f"Revenue from {order.name}",
                    'sale_order_id': order.id,
                    'amount': order.amount_total,
                    'customer': order.partner_id.id,
                    'date': fields.Date.today(),
                    'trip_id': order.trip_id.id if order.trip_id else False,
                    'payment_status': 'not_paid',
                }
                
                # Determine revenue type based on products
                if order.order_line:
                    product_name = order.order_line[0].product_id.name.lower()
                    if 'cargo' in product_name or 'freight' in product_name:
                        revenue_vals['revenue_type'] = 'cargo_transport'
                    elif 'passenger' in product_name:
                        revenue_vals['revenue_type'] = 'passenger_transport'
                    else:
                        revenue_vals['revenue_type'] = 'other'
                
                self.env['transport.trip.revenue'].create(revenue_vals)
        
        return result
    
    def action_view_transport_revenues(self):
        """Action to view related transport revenues"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Revenues from {self.name}',
            'res_model': 'transport.trip.revenue',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {
                'default_sale_order_id': self.id,
                'default_customer': self.partner_id.id,
                'default_trip_id': self.trip_id.id if self.trip_id else False,
            }
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Add any transport-specific fields for order lines if needed
    passenger_count = fields.Integer(
        string='Number of Passengers',
        help="Number of passengers for passenger transport service",
        default=1
    )
    
    cargo_weight = fields.Float(
        string='Cargo Weight (kg)',
        help="Weight of cargo for freight transport service"
    )
