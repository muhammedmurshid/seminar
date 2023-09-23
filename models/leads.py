from odoo import api, fields, models, _


class SeminarLeads(models.Model):
    _name = 'seminar.leads'
    _description = 'Seminar Leads'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'college_id'

    college_id = fields.Many2one('college.list', string='College/School', required=True)
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other')],

                                string='District', required=True)
    booked_by = fields.Many2one('hr.employee', string='Booked By')
    attended_by = fields.Many2one('hr.employee', string='Attended By')
    seminar_ids = fields.One2many('seminar.students', 'seminar_id', string='Seminar')
    lead_source_id = fields.Many2one('leads.sources', string='Lead Source', required=True)
    stream = fields.Char(string='Stream')
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done')
    ], string='Status', default='draft')
    # course = fields.Char(string='Course', required=1)
    school = fields.Selection([('hsc', 'HSC'), ('ssc', 'SSC')], string='School')
    reference_no = fields.Char(string='Leads Number', required=True,
                               readonly=True, default=lambda self: _('New'))

    @api.depends('seminar_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.seminar_ids)

    child_count = fields.Integer(string='Lead Count', compute='_compute_child_count', store=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'seminar.leads') or _('New')
        res = super(SeminarLeads, self).create(vals)
        return res

    def action_done_leads_manager(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('leads.mail_seminar_leads_done').id)])
        activity_id.action_feedback('done')
        # activity_id.sudo().unlink()
        self.activity_done = True

    activity_done = fields.Boolean(string='Done')

    def action_submit(self):
        self.state = 'done'
        preferred_course = ""

        for rec in self.seminar_ids:
            preferred_course = ""
            if rec.preferred_course:
                preferred_course += rec.preferred_course.name
            else:
                preferred_course += 'None'
            self.env['leads.logic'].sudo().create({
                'leads_source': self.lead_source_id.id,
                'phone_number': rec.contact_number,
                'name': rec.student_name,
                'lead_owner': self.create_uid.employee_id.id,
                'place': rec.place,
                'college_name': self.college_id.college_name,
                # 'last_studied_course': self.course,
                'seminar_lead_id': rec.id,
                'email_address': rec.email_address,
                'course_id': preferred_course,
                'lead_quality': 'Interested',
                'district': self.district,
                'phone_number_second': rec.whatsapp_number,
                'parent_number': rec.parent_number
            })
        res_user = self.env['res.users'].search([])
        leads = self.env['leads.logic'].search([])
        for user in res_user:
            if user.has_group('leads.leads_admin'):
                print(user.name, 'user')
                self.activity_schedule(
                    'leads.mail_seminar_leads_done', user_id=user.id,
                    note=f'Seminar data of {self.college_id.college_name} having {self.child_count} leads is submitted by {self.create_uid.name} '),

    @api.depends('seminar_ids.incentive')
    def _total_incentive_amount(self):
        total = 0
        for rec in self.seminar_ids:
            total += rec.incentive
        self.update({
            'incentive_amt': total
        })

    incentive_amt = fields.Float(string='Incentive', compute='_total_incentive_amount', store=True)

    class CollegeListsLeads(models.Model):
        _name = 'seminar.students'

        student_name = fields.Char(string='Student Name', required=True)
        contact_number = fields.Char(string='Contact Number', required=True)
        whatsapp_number = fields.Char(string='Whatsapp Number')
        seminar_id = fields.Many2one('seminar.leads', string='Seminar', ondelete='cascade')
        place = fields.Char(string='Place')
        admission_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Admission Status', readonly=True,
                                            default='no')
        email_address = fields.Char(string='Email Address')
        parent_number = fields.Char(string='Parent Number')
        preferred_course = fields.Many2one('logic.base.courses', string='Preferred Course')

        @api.depends('student_name')
        def _compute_seminar_executive(self):
            res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
            if res_user.has_group('seminar.seminar_executive'):
                self.make_visible_seminar_executive = True
            else:
                self.make_visible_seminar_executive = False

        make_visible_seminar_executive = fields.Boolean(string="Executive", compute='_compute_seminar_executive')

        @api.depends('incentive', 'student_name')
        def _total_incentive(self):
            ss = self.env['seminar.lead.incentive'].search([])
            for rec in ss:
                self.incentive = rec.incentive_per_lead

        incentive = fields.Float(string='Incentive', compute='_total_incentive', store=True)

    class SeminarLeadIncentive(models.Model):
        _name = 'seminar.lead.incentive'
        _description = 'Incentive Amount'
        _inherit = ['mail.thread', 'mail.activity.mixin']
        _rec_name = 'incentive_per_lead'

        incentive_per_lead = fields.Float(string='Incentive per lead')
