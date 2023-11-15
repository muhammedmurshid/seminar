from odoo import fields, models, _, api


class SeminarCipRecords(models.Model):
    _name = 'seminar.cip.records'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'CIP Records'

    seminar_user_id = fields.Many2one('res.users', string='Seminar User')
    seminar_cip_ids = fields.One2many('seminar.cip.list', 'cip_id', string='CIP')
    state = fields.Selection(
        [('draft', 'Draft'), ('hr_approval', 'HR Approval'), ('register_payment', 'Register Payment'),
         ('paid', 'Paid'), ('rejected', 'Rejected')], string='Status', default='draft', tracking=True
    )
    date = fields.Date(string='Date', default=lambda self: fields.Date.today())

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.seminar_user_id.name + " " + 'Cip Record'

    @api.depends('seminar_cip_ids.net_hour')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.seminar_cip_ids:
            total += order.net_hour
        self.update({
            'total_cip_duration': total,

        })

    total_cip_duration = fields.Float(string='Total Duration', compute='_amount_all', store=True)

    @api.depends('total_cip_duration')
    def _compute_cip_payment(self):
        rate = self.env['cip.executive.rate'].sudo().search([], limit=1)
        for i in self:
            i.cip_payment = i.total_cip_duration * rate.cip_rate

    cip_payment = fields.Float(string='CIP Payment', compute='_compute_cip_payment', store=True)
    payment_date = fields.Date(string='Payment Date')
    marketing_head = fields.Many2one('res.users', string='Marketing Head', default=lambda self: self.env.user)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def action_sent_to_approve(self):
        for i in self:
            user = self.env.ref('seminar.seminar_admin').users

            for j in user:
                print(j.name, 'admin')
                i.activity_schedule('seminar.seminar_cip_payment_activity', user_id=j.id,
                                    note=f' {self.marketing_head.name} has requested for Cip payment for {self.seminar_user_id.name}')
        self.state = 'hr_approval'

    def action_approve(self):
        self.env['payment.request'].sudo().create({
            'source_type': 'other',
            'source_user': self.seminar_user_id.id,
            'amount': self.cip_payment,
            'description': 'Cip Payment',
            'cip_rec_id': self.id,
            'cip_rec_name': 'Cip Records',
            # 'payment_expect_date': self.payment_expected_date,
            # 'seminar_source': self.id,
            # 'account_name': self.lead_user_id.employee_id.name_as_per_bank,
            # 'account_no': self.lead_user_id.employee_id.bank_acc_number,
            # 'ifsc_code': self.lead_user_id.employee_id.ifsc_code,
            # 'bank_name': self.lead_user_id.employee_id.bank_name,
            # 'bank_branch': self.lead_user_id.employee_id.branch_bank,
            # 'seminar_executive': self.seminar_user.id

        })
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('seminar.seminar_cip_payment_activity').id)])
        activity_id.action_feedback(feedback=f'Cip payment request approved.')

        self.state = 'register_payment'

    def action_reject(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('seminar.seminar_cip_payment_activity').id)])
        activity_id.action_feedback(feedback=f'Cip payment request rejected.')
        self.state = 'rejected'


class SeminarCipLists(models.Model):
    _name = 'seminar.cip.list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'CIP Lists'

    date = fields.Date(string='Date')
    net_hour = fields.Float(string='Net Hour')
    institute_name = fields.Char(string='Institute Name')
    cip_id = fields.Many2one('seminar.cip.records', string='CIP')
    location = fields.Char(string='Location')


class CipExecutiveRate(models.Model):
    _name = 'cip.executive.rate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'CIP Executive Rate'

    cip_rate = fields.Float(string='CIP Rate')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def _compute_display_name(self):
        for record in self:
            record.display_name = 'Cip Record' + ' ' + str(record.cip_rate)


class CipPaymentId(models.Model):
    _inherit = 'payment.request'

    cip_rec_id = fields.Many2one('seminar.cip.records', string='CIP')
    cip_rec_name = fields.Char(string='CIP Name')
