from odoo import fields, models, api, _


class IncentiveLeadsRecords(models.Model):
    _name = 'seminar.lead.incentive.records'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Incentive Leads'
    _rec_name = 'display_name'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    lead_user_id = fields.Many2one('res.users', string='Lead User', required=True)
    seminar_ids = fields.Many2many('seminar.leads', string='Seminar')
    state = fields.Selection(
        [('draft', 'Draft'), ('hr_approval', 'HR Approval'),
         ('payment_requested', 'Payment Requested'), ('paid', 'Paid'), ('rejected', 'Rejected')],
        string='Status', default='draft', tracking=True)
    payment_date = fields.Date(string='Payment Date')
    leads_list_ids = fields.One2many('incentive.leads.list', 'leads_list_id', string='Leads List')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    def _compute_display_name(self):
        for i in self:
            i.display_name = str(i.lead_user_id.name) + " " + 'Leads Incentive'

    @api.onchange('lead_user_id', 'date_from', 'date_to')
    def onchange_lead_user_id(self):
        self.seminar_ids = False
        ss = self.env['seminar.leads'].sudo().search([])
        unlink_commands = [(3, child.id) for child in self.leads_list_ids]
        self.write({'leads_list_ids': unlink_commands})
        record = []
        for rec in ss:
            if rec.seminar_date:
                if self.date_from and self.date_to:
                    if self.date_from <= rec.seminar_date <= self.date_to:
                        print(rec.reference_no, 'datas')
                        print(rec.booked_by.user_id.name, 'user')
                        if self.lead_user_id.id == rec.attended_by.user_id.id and self.lead_user_id.id == rec.booked_by.user_id.id:
                            if rec.incentive_booked == False and rec.incentive_attended == False:
                                if rec.child_count < 10:
                                    res_list = {
                                        'date': rec.seminar_date,
                                        'incentive_amount': 100,
                                        # 'user_id': rec.booked_by.user_id.id,
                                        'both': rec.booked_by.user_id.id,
                                        'record_id': rec.id,
                                        'stream': rec.stream,
                                        'total_lead_count': rec.child_count
                                        # 'attended_by': rec.attended_by.user_id.id,

                                    }
                                    record.append((0, 0, res_list))
                                    print('both')
                                else:
                                    res_list = {
                                        'date': rec.seminar_date,
                                        'incentive_amount': rec.child_count * 10 /2,
                                        # 'user_id': rec.booked_by.user_id.id,
                                        'both': rec.booked_by.user_id.id,
                                        'record_id': rec.id,
                                        'stream': rec.stream,
                                        'total_lead_count': rec.child_count
                                        # 'attended_by': rec.attended_by.user_id.id,

                                    }
                                    record.append((0, 0, res_list))
                                    print('both')
                        if self.lead_user_id.id == rec.booked_by.user_id.id:
                            if rec.booked_by.id != rec.attended_by.id:
                                if rec.incentive_booked == False:
                                    if rec.child_count > 10:
                                        res_list = {
                                            'date': rec.seminar_date,
                                            'incentive_amount': rec.child_count * 10 / 2,
                                            # 'user_id': rec.booked_by.user_id.id,
                                            'booked_by': rec.booked_by.user_id.id,
                                            'booked_count': rec.child_count / 2,
                                            # 'attended_by': rec.attended_by.user_id.id,
                                            'record_id': rec.id,
                                            'stream': rec.stream
                                            # 'attended_by': rec.attended_by.user_id.id,

                                        }
                                        record.append((0, 0, res_list))
                                        print('booked')
                                    else:
                                        res_list = {
                                            'date': rec.seminar_date,
                                            'incentive_amount': 50,
                                            # 'user_id': rec.booked_by.user_id.id,
                                            'booked_by': rec.booked_by.user_id.id,
                                            'booked_count': rec.child_count / 2,
                                            # 'attended_by': rec.attended_by.user_id.id,
                                            'record_id': rec.id,
                                            'stream': rec.stream
                                            # 'attended_by': rec.attended_by.user_id.id,

                                        }
                                        record.append((0, 0, res_list))
                                        print('booked')
                        if self.lead_user_id.id == rec.attended_by.user_id.id:
                            if rec.booked_by.id != rec.attended_by.id:
                                if rec.incentive_attended == False:
                                    if rec.child_count > 10:
                                        res_list = {
                                            'date': rec.seminar_date,
                                            'incentive_amount': rec.incentive_amt / 2,
                                            # 'user_id': rec.booked_by.user_id.id,
                                            # 'booked_by': rec.booked_by.user_id.id,
                                            'attended_by': rec.attended_by.user_id.id,
                                            'record_id': rec.id,
                                            'attended_count': rec.child_count / 2,
                                            'stream': rec.stream
                                            # 'attended_by': rec.attended_by.user_id.id,

                                        }
                                        record.append((0, 0, res_list))
                                        print('attend')
                                    else:
                                        res_list = {
                                            'date': rec.seminar_date,
                                            'incentive_amount': 50,
                                            # 'user_id': rec.booked_by.user_id.id,
                                            # 'booked_by': rec.booked_by.user_id.id,
                                            'attended_by': rec.attended_by.user_id.id,
                                            'record_id': rec.id,
                                            'attended_count': rec.child_count / 2,
                                            'stream': rec.stream
                                            # 'attended_by': rec.attended_by.user_id.id,

                                        }
                                        record.append((0, 0, res_list))
                                        print('attend')

        self.update({
            # 'state': 'sent_approval',
            'leads_list_ids': record

        })

    @api.depends('leads_list_ids.incentive_amount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.leads_list_ids:
            total += order.incentive_amount
        self.update({
            'incentive_amount': total,

        })

    incentive_amount = fields.Float(string='Incentive Amount', compute='_amount_all', store=True)

    @api.depends('leads_list_ids.total_lead_count')
    def _lead_count_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.leads_list_ids:
            total += order.total_lead_count
        self.update({
            'lead_count': total,

        })

    lead_count = fields.Float(string='Both Lead Count', compute='_lead_count_all', store=True)

    @api.depends('leads_list_ids.attended_count')
    def _lead_count_attended(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.leads_list_ids:
            total += order.attended_count
        self.update({
            'attended_lead_count': total,

        })

    attended_lead_count = fields.Float(string='Attended Lead Count', compute='_lead_count_attended', store=True)

    @api.depends('leads_list_ids.booked_count')
    def _lead_count_booked(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.leads_list_ids:
            total += order.booked_count
        self.update({
            'booked_lead_count': total,

        })

    booked_lead_count = fields.Float(string='Booked Lead Count', compute='_lead_count_booked', store=True)

    @api.depends('booked_lead_count', 'attended_lead_count', 'lead_count')
    def _total_leads_count(self):
        for i in self:
            i.total_leads_count = i.booked_lead_count + i.attended_lead_count + i.lead_count

    total_leads_count = fields.Float(string='Total Leads Count', compute='_total_leads_count', store=True)

    def action_sent_to_approve(self):
        for i in self:
            user = self.env.ref('seminar.seminar_admin').users
            for j in user:
                print(j.name, 'admin')
                i.activity_schedule('seminar.seminar_incentive_activity', user_id=j.id,
                                    note=f' {self.lead_user_id.name} has requested for Incentive')
        self.state = 'hr_approval'

    def action_hr_approval(self):
        for rec in self.leads_list_ids:
            print(rec.id, 'id')
            if rec.both:
                print(rec.id, 'both')
                rec.record_id.incentive_booked = True
                rec.record_id.incentive_attended = True
            if rec.booked_by:
                print(rec.id, 'booked')
                rec.record_id.incentive_booked = True
            if rec.attended_by:
                print(rec.id, 'attend')
                rec.record_id.incentive_attended = True

        self.env['payment.request'].sudo().create({
            'source_type': 'other',
            'source_user': self.create_uid.id,
            'amount': self.incentive_amount,
            'description': 'Seminar Incentive',
            'seminar_incentive_source': self.id,

        })
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('seminar.seminar_incentive_activity').id)])
        activity_id.action_feedback(feedback=f'Incentive request approved.')

        for i in self:
            user = self.env.ref('seminar.seminar_accounts').users
            for j in user:
                print(j.name, 'accounts')
                i.activity_schedule('seminar.seminar_incentive_activity', user_id=j.id,
                                    note=f' {self.lead_user_id.name} has requested for Incentive')
        self.state = 'payment_requested'

    def action_rejected(self):
        self.state = 'rejected'

    def action_return_to_draft(self):
        self.state = 'draft'

    def remove_paid_seminar_incentive_records(self):
        print('remove')
        refund_record = self.env['seminar.lead.incentive.records'].search([])
        users = self.env.ref('seminar.seminar_accounts').users
        for i in users:
            print(i.name, 'lll')
            for record in refund_record:
                if record.state == 'paid':
                    activity_id = record.env['mail.activity'].search(
                        [('res_id', '=', record.id), ('user_id', '=', i.id), (
                            'activity_type_id', '=', self.env.ref('seminar.seminar_incentive_activity').id)])
                    activity_id.unlink()


class IncentiveEmployeeLists(models.Model):
    _name = 'incentive.leads.list'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', string='User')
    booked_by = fields.Many2one('res.users', string='Booked By')
    attended_by = fields.Many2one('res.users', string='Attended By')
    both = fields.Many2one('res.users', string='Both')
    date = fields.Date(string='Date')
    stream = fields.Char(string='Stream')
    record_id = fields.Many2one('seminar.leads', string='Record')
    incentive_amount = fields.Float(string='Incentive Amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    total_lead_count = fields.Float(string='Total Lead Count')
    booked_count = fields.Float(string='Booked Count')
    attended_count = fields.Float(string='Attended Count')
    leads_list_id = fields.Many2one('seminar.lead.incentive.records', string='Incentive Leads', ondelete='cascade')
