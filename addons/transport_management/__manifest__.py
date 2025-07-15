{
    'name': 'Transport Management',
    'version': '18.0.1.0.0',
    'summary': 'Complete Transport Management System for Morocco-France Routes',
    'description': """
        Transport Management System for International Routes
        
        Features:
        - Vehicle fleet management (trucks, buses)
        - Driver and staff management
        - Trip management between Morocco and France
        - Cost tracking and profit calculation
        - Revenue management
        - Expense tracking (fuel, tolls, customs, accommodation)
        - Comprehensive reporting
        - Maintenance alerts
    """,
    'author': 'Transport STE',
    'website': 'https://www.transport-ste.com',
    'category': 'Operations/Fleet',
    'depends': [
        'base',
        'fleet',
        'hr',
        'mail',
        'portal',
        'sale',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/trip_data.xml',
        'data/transport_products.xml',
        'views/transport_dashboard_views.xml',
        'views/trip_views.xml',
        'views/trip_expense_views.xml',
        'views/trip_revenue_views.xml',
        'views/sale_order_views.xml',
        'views/fleet_vehicle_model_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/hr_employee_views.xml',
        'views/menus.xml',
        'reports/trip_report.xml',
        'reports/profit_analysis_report.xml',
        
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'transport_management/static/src/js/transport_dashboard.js',
            'transport_management/static/src/xml/transport_dashboard.xml',
            'transport_management/static/src/css/transport_dashboard.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
