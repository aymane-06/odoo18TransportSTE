#!/usr/bin/env python3
import odoo
from odoo.api import Environment
import os

# Set up Odoo configuration
odoo.tools.config.parse_config(['-d', 'odoo18TransportSTE'])

# Initialize registry
with odoo.registry('odoo18TransportSTE').cursor() as cr:
    env = Environment(cr, 1, {})  # Using admin user (uid=1)
    
    # Find and upgrade the transport_management module
    module = env['ir.module.module'].search([('name', '=', 'transport_management')])
    if module:
        print(f"Found module: {module.name} (state: {module.state})")
        print("Upgrading module...")
        module.button_immediate_upgrade()
        print("Module upgraded successfully!")
    else:
        print("Module 'transport_management' not found")
