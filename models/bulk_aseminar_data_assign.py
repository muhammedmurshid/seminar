from odoo import models, fields, api, _


class BulkSeminarDataAssign(models.TransientModel):
    _name = 'bulk.seminar.assign'
    _description = 'Bulk Seminar Data Assign'

    seminar_id = fields.Many2one('seminar.leads', string='Seminar')

    @api.onchange('seminar_id')
    def _onchange_leads_users(self):
        users = self.env.ref('leads.leads_basic_user').users
        lead_users = []
        for j in users:
            print(j.name, 'j')
            lead_users.append(j.id)
        domain = [('id', 'in', lead_users)]
        return {'domain': {'user_id': domain}}

    user_id = fields.Many2one('res.users', string='Assign To', domain=_onchange_leads_users, required=1)

    def action_assign(self):
        lead = self.env['leads.logic'].sudo().search([('seminar_id', '=', self.seminar_id.id)])

        for rec in lead:
            if rec:
                rec.update({
                    'leads_assign': self.user_id.employee_id.id,
                    'state': 'confirm'
                })
            # seminar_data = self.env['seminar.students'].sudo().search([('id', '=', rec.seminar_lead_id)])
            # for j in seminar_data:
            #     print(j.seminar_id, 'rec')
            #     print(rec.id, 'lead')
            #     rec.update({
            #         'leads_assign': self.user_id.employee_id.id,
            #         'state': 'confirm'
            #     })

                # rec.activity_schedule('leads.mail_seminar_leads_done', user_id=self.user_id.id)

            # rec.lead_assign = self.user_id.employee_id.id
        self.seminar_id.bulk_lead_assign = True
        self.seminar_id.state = 'leads_assigned'

