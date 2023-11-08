from odoo import fields, models, api, _


class IncentiveLeadsRecords(models.Model):
    _name = 'seminar.lead.incentive.records'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Incentive Leads'
    _rec_name = 'lead_user_id'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    lead_user_id = fields.Many2one('res.users', string='User')
    incentive_amount = fields.Float(string='Incentive Amount')
    seminar_ids = fields.Many2many('seminar.leads', string='Seminar')
    state = fields.Selection(
        [('draft', 'Draft'), ('sent_approval', 'Sent to Approve'), ('hr_approval', 'HR Approval'),
         ('payment_requested', 'Payment Requested'), ('paid', 'Paid'), ('rejected', 'Rejected')],
        string='Status', default='draft', tracking=True)
    payment_date = fields.Date(string='Payment Date')
    leads_list_ids = fields.One2many('incentive.leads.list', 'leads_list_id', string='Leads List')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def total_incentive(self):
        self.seminar_ids = False
        ss = self.env['seminar.leads'].sudo().search([])
        unlink_commands = [(3, child.id) for child in self.leads_list_ids]
        self.write({'leads_list_ids': unlink_commands})
        total = 0
        for rec in ss:
            record = []
            if rec.seminar_date:
                if self.date_from <= rec.seminar_date <= self.date_to:
                    if rec.attended_by.id == rec.booked_by.id:
                        print(rec.seminar_date, 'date')
                        res_list = {
                            'date': rec.seminar_date,
                            'incentive_amount': rec.incentive_amt,
                            # 'user_id': rec.booked_by.user_id.id,
                            'both': rec.booked_by.user_id.id,
                            'record_id': rec.id,
                            # 'attended_by': rec.attended_by.user_id.id,

                        }
                        record.append((0, 0, res_list))
                    else:
                        res_list = {
                            'date': rec.seminar_date,
                            'incentive_amount': rec.incentive_amt / 2,
                            # 'user_id': rec.booked_by.user_id.id,
                            'booked_by': rec.booked_by.user_id.id,
                            'attended_by': rec.attended_by.user_id.id,
                            'record_id': rec.id,
                            # 'attended_by': rec.attended_by.user_id.id,

                        }
                        record.append((0, 0, res_list))
                    # if self.lead_user_id == rec.booked_by.user_id and self.lead_user_id == rec.attended_by.user_id and rec.state == 'done':
                    total_amount = sum(rec.mapped('incentive_amt'))
                    print(rec.id, 'total')
                    total += total_amount
                    self.write({
                        'seminar_ids': [(4, rec.id)]
                    })

                    # elif self.lead_user_id == rec.booked_by.user_id and rec.state == 'done':
                    #     total_amount = sum(rec.mapped('incentive_amt')) / 2
                    #     print(rec.id, 'total')
                    #     total += total_amount
                    #     self.write({
                    #         'seminar_ids': [(4, rec.id)]
                    #     })
                    # elif self.lead_user_id == rec.attended_by.user_id and rec.state == 'done':
                    #     total_amount = sum(rec.mapped('incentive_amt')) / 2
                    #     print(rec.id, 'total')
                    #     total += total_amount
                    #
                    #     self.write({
                    #         'seminar_ids': [(4, rec.id)]
                    #     })
            self.update({
                'incentive_amount': total,
                'state': 'sent_approval',
                'leads_list_ids': record

            })

    def action_sent_to_approve(self):
        for i in self:
            user = self.env.ref('seminar.seminar_admin').users

            for j in user:
                print(j.name, 'admin')
                i.activity_schedule('seminar.seminar_incentive_activity', user_id=j.id,
                                    note=f' {self.lead_user_id.name} has requested for Incentive')
        self.state = 'hr_approval'

    def action_hr_approval(self):
        self.env['payment.request'].sudo().create({
            'source_type': 'other',
            'source_user': self.create_uid.id,
            'amount': self.incentive_amount,
            'description': 'Seminar Incentive',
            'seminar_incentive_source': self.id,
            # 'payment_expect_date': self.payment_expected_date,
            # 'seminar_source': self.id,
            'account_name': self.lead_user_id.employee_id.name_as_per_bank,
            'account_no': self.lead_user_id.employee_id.bank_acc_number,
            'ifsc_code': self.lead_user_id.employee_id.ifsc_code,
            'bank_name': self.lead_user_id.employee_id.bank_name,
            'bank_branch': self.lead_user_id.employee_id.branch_bank,
            # 'seminar_executive': self.seminar_user.id

        })
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('seminar.seminar_incentive_activity').id)])
        activity_id.action_feedback(feedback=f'Incentive request approved.')
        self.state = 'payment_requested'

    def action_rejected(self):
        self.state = 'rejected'

    def action_return_to_draft(self):
        self.state = 'draft'


class IncentiveEmployeeLists(models.Model):
    _name = 'incentive.leads.list'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', string='User')
    booked_by = fields.Many2one('res.users', string='Booked By')
    attended_by = fields.Many2one('res.users', string='Attended By')
    both = fields.Many2one('res.users', string='Both')
    date = fields.Date(string='Date')
    record_id = fields.Many2one('seminar.leads', string='Record')
    incentive_amount = fields.Float(string='Incentive Amount')
    leads_list_id = fields.Many2one('seminar.lead.incentive.records', string='Incentive Leads', ondelete='cascade')
