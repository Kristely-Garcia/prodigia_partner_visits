# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Registro de visitas a empresas',
    'version': '0.1.0',
    'category': 'Sales',
    'depends': ['sale','base_geolocalize'],
    'author': 'Prodigia',
    'summary': 'Crea registro de visitas a empresas',
    'description': 
    '''
    Crea registro de visitas a empresas
    utilizando google maps
    ''',
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/partner_visit_views.xml',
        'views/report_views.xml',
        'views/templates.xml',
        'views/config_views.xml',
        'wizard/wizard_views.xml',
    ],
    'qweb': [
        'static/src/xml/js_qweb_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
