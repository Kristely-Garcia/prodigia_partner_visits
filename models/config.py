# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    distance_treshold = fields.Float(string="distancia maxima",
        default=50,
        help="define la distancia maxima aceptada entre 2 puntos geograficos")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    distance_treshold = fields.Float(related="company_id.distance_treshold")
    g_map_widget_api_key = fields.Char(string='Llave API de Google Maps para widget',
        help="para usarse en widget g_map")


    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        ICPSudo.set_param('google.api_key_geocode',
                          self.g_map_widget_api_key)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update({
            'g_map_widget_api_key': ICPSudo.get_param(
                'google.api_key_geocode', default=''),
        })
        return res