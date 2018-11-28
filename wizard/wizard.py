# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PartnerVisitWizard(models.TransientModel):
    _name = "partner.visit.wizard"

    start_date = fields.Date("Fecha inicial", required=True)
    end_date = fields.Date("Fecha final", required=True)
    partner_id = fields.Many2one('res.partner', 'Empresa',required=False)
    user_id = fields.Many2one('res.users', 'Vendedor',required=False)
    
    
    @api.multi
    def _check_dates(self):
        """
        VALIDA QUE LA FECHA FINAL NO SEA ANTES QUE LA INICIAL
        """
        if self.end_date < self.start_date:
            return False
        return True

    _constraints = [
        (_check_dates, 'La fecha final no puede ser menor a la inicial!', ['end_date'])
    ]

    # GENERA EL DOMINIO DE BUSQUEDA
    # DEPENDIENDO DE LOS CAMPOS
    # LLENADOS DEL FORMULARIO
    def get_search_domain(self):
        domain = [
                #('partner_id','=',self.partner_id.id),
                ('state','=','hecho'),
                ('date','>=',self.start_date),
                ('date','<=',self.end_date),
                ]
        if self.user_id:
            domain.append(('user_id','=',self.user_id.id),)
        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        return domain


    # GENERA DATOS DEL REPORTE
    def button_generate(self):
        PartnerVisit = self.env['partner.visit']
        VisitUserReport = self.env['visit.user.report']
        VisitUserReportLine = self.env['visit.user.report.line']

        domain = self.get_search_domain()
        res = PartnerVisit.search(domain, order='date')

        if not res:
            raise ValidationError(_('Los parametros seleccionados actualmente\
             no generan informacion para el reporte, intene modificarlos.'))

        name = 'Reporte de visitas'
        if self.user_id:
            name = 'Visitas realizadas por %s'%(self.user_id.partner_id.name)

        report = VisitUserReport.create(
            {'name': name,
            'start_date':self.start_date,
            'end_date':self.end_date,
            'partner_id':self.partner_id.id,
            'user_id':self.user_id.id,
            #'line_ids':xlines,
            })

        xlines = []
        for visit in res:
            vals = {
                'report_base_id':report.id,
                'partner_visit_id':visit.id,
            }
            line = (0,0,vals)
            xlines.append(line)
        print('1111')
        report.write({'line_ids':xlines})
        

        #VISTA
        action = self.env.ref('prodigia_partner_visits.action_visit_user_report').read()[0]
        #action['domain'] = [('id','=',report.id)]
        action['res_id'] = report.id
        return action

    # @api.multi
    # def action_view_invoice(self):
    #     invoices = self.mapped('invoice_ids')
    #     action = self.env.ref('account.action_invoice_tree1').read()[0]
    #     if len(invoices) > 1:
    #         action['domain'] = [('id', 'in', invoices.ids)]
    #     elif len(invoices) == 1:
    #         action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
    #         action['res_id'] = invoices.ids[0]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action
