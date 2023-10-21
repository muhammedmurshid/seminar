from odoo import api, fields, models, _


class SeminarLeads(models.Model):
    _name = 'seminar.leads'
    _description = 'Seminar Leads'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'college_id'

    college_id = fields.Many2one('college.list', string='Institute Name')
    lead_source_id = fields.Many2one('leads.sources', string='Lead Source', required=True)
    lead_sc_name = fields.Char(string='Lead Sc Name', related='lead_source_id.name')
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other')],
                                string='District')
    booked_by = fields.Many2one('hr.employee', string='Booked By')
    seminar_date = fields.Date(string='Date')
    attended_by = fields.Many2one('hr.employee', string='Attended By')
    seminar_ids = fields.One2many('seminar.students', 'seminar_id', string='Seminar')
    coordinator_id = fields.Many2one('hr.employee', string='Programme Coordinator')
    hosted_by_id = fields.Many2one('hr.employee', string='Hosted By')
    stream = fields.Char(string='Stream')
    seminar_duplicate_ids = fields.One2many('duplicate.record.seminar', 'seminar_duplicate_id', string='Seminar')
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done')
    ], string='Status', default='draft', tracking=True)
    # course = fields.Char(string='Course', required=1)
    school = fields.Selection([('hsc', 'HSC'), ('ssc', 'SSC')], string='School')
    reference_no = fields.Char(string='Leads Number', required=True,
                               readonly=True, default=lambda self: _('New'))
    count_duplicate = fields.Integer(string='Count Duplicate', compute='_compute_count_duplicate', store=True)

    @api.depends('seminar_duplicate_ids')
    def _compute_count_duplicate(self):
        for record in self:
            record.count_duplicate = len(record.seminar_duplicate_ids)

    @api.depends('seminar_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.seminar_ids)

    child_count = fields.Integer(string='Lead Count', compute='_compute_child_count', store=True)

    @api.depends('child_count', 'count_duplicate')
    def _compute_total_leads_count(self):
        for record in self:
            record.count = record.child_count + record.count_duplicate

    count = fields.Integer(string='Total Leads', compute='_compute_total_leads_count', store=True)

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
            if self.lead_sc_name == 'Seminar':
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
                    'base_course_id': rec.preferred_course.id,
                    'lead_quality': 'nill',
                    'district': self.district,
                    'phone_number_second': rec.whatsapp_number,
                    'parent_number': rec.parent_number
                })
            else:
                self.env['leads.logic'].sudo().create({
                    'leads_source': self.lead_source_id.id,
                    'phone_number': rec.contact_number,
                    'name': rec.student_name,
                    'lead_owner': self.create_uid.employee_id.id,
                    'place': rec.place,
                    'college_name': 'nill',
                    # 'last_studied_course': self.course,
                    'seminar_lead_id': rec.id,
                    'email_address': rec.email_address,
                    'base_course_id': rec.preferred_course.id,
                    'lead_quality': 'nill',
                    'district': rec.district,
                    'phone_number_second': rec.whatsapp_number,
                    'parent_number': rec.parent_number
                })
        for request in self.seminar_duplicate_ids:
            if request.district:
                self.env['re_allocation.request.leads'].sudo().create({
                    'leads_source': self.lead_source_id.id,
                    'phone_number': request.contact_number,
                    'name': request.student_name,
                    'duplicate_record_id': request.id,
                    'lead_owner': self.create_uid.employee_id.id,
                    'place': request.place,
                    'college_name': 'nill',
                    # 'last_studied_course': self.course,
                    'seminar_lead_id': request.id,
                    'email_address': request.email_address,
                    'base_course_id': request.preferred_course.id,
                    'lead_quality': 'Interested',
                    'district': request.district,
                    'phone_number_second': request.whatsapp_number,
                    'parent_number': request.parent_number
                })
            else:
                self.env['re_allocation.request.leads'].sudo().create({
                    'leads_source': self.lead_source_id.id,
                    'phone_number': request.contact_number,
                    'name': request.student_name,
                    'duplicate_record_id': request.id,
                    'lead_owner': self.create_uid.employee_id.id,
                    'place': request.place,
                    'college_name': self.college_id.college_name,
                    # 'last_studied_course': self.course,
                    'seminar_lead_id': request.id,
                    'email_address': request.email_address,
                    'base_course_id': request.preferred_course.id,
                    'lead_quality': 'Interested',
                    'district': self.district,
                    'phone_number_second': request.whatsapp_number,
                    'parent_number': request.parent_number
                })
        res_user = self.env['res.users'].search([])
        leads = self.env['leads.logic'].search([])
        for user in res_user:
            if user.has_group('leads.leads_admin'):
                print(user.name, 'user')
                self.activity_schedule(
                    'leads.mail_seminar_leads_done', user_id=user.id,
                    note=f'Seminar data of {self.college_id.college_name} having {self.child_count} leads is submitted by {self.create_uid.name} '),
        self.env['mail.mail'].sudo().create({
            'model': 'seminar.leads',
            'subject': 'Seminar Leads',
            'body_html': f'{self.create_uid.name} submitted leads of {self.college_id.college_name} containing {self.child_count} leads',
            'email_to': self.create_uid.employee_id.parent_id.work_email,
        }).send()

    @api.depends('seminar_ids.incentive', 'seminar_duplicate_ids.selected_lead')
    def _total_incentive_amount(self):
        total = 0
        for rec in self.seminar_ids:
            total += rec.incentive
        for duplicate in self.seminar_duplicate_ids:
            total += duplicate.incentive
        self.update({
            'incentive_amt': total
        })

    incentive_amt = fields.Float(string='Incentive', compute='_total_incentive_amount', store=True)

    def action_add_to_duplicates(self):
        record_duplicate = []
        for duplicate in self.seminar_ids:
            leads_rec = self.env['leads.logic'].sudo().search([('phone_number', '=', duplicate.contact_number)])
            print(duplicate, 'duplicate')
            if duplicate.contact_number:
                if leads_rec:
                    res_list = {
                        'student_name': duplicate.student_name,
                        'contact_number': duplicate.contact_number,
                        'district': duplicate.district,
                        'preferred_course': duplicate.preferred_course.id,
                        'whatsapp_number': duplicate.whatsapp_number,
                        'parent_number': duplicate.parent_number,
                        'email_address': duplicate.email_address,
                        'place': duplicate.place,

                    }
                    record_duplicate.append((0, 0, res_list))
                    duplicate.unlink()
        print(record_duplicate, 'record_duplicate')
        self.seminar_duplicate_ids = record_duplicate

    @api.depends('seminar_duplicate_ids.selected_lead')
    def _compute_selected_duplicates_count(self):
        for record in self:
            record.selected_duplicates_count = len(record.seminar_duplicate_ids.filtered(lambda x: x.selected_lead))

    selected_duplicates_count = fields.Integer(compute='_compute_selected_duplicates_count', store=True,
                                               string='Selected Duplicates')


class CollegeListsLeads(models.Model):
    _name = 'seminar.students'

    student_name = fields.Char(string='Student Name', required=True)
    contact_number = fields.Char(string='Contact Number', required=True, default='+91')
    whatsapp_number = fields.Char(string='Whatsapp Number')
    seminar_id = fields.Many2one('seminar.leads', string='Seminar', ondelete='cascade')
    place = fields.Char(string='Place')
    admission_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Admission Status', readonly=True,
                                        default='no')
    email_address = fields.Char(string='Email Address')
    parent_number = fields.Char(string='Parent Number')
    lead_sc_name = fields.Char(string='Lead Source', related='seminar_id.lead_sc_name')
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other')],
                                string='District')
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


class DuplicateRecord(models.TransientModel):
    _name = 'duplicate.record.seminar'

    student_name = fields.Char(string='Student Name', required=True)
    contact_number = fields.Char(string='Contact Number', required=True)
    whatsapp_number = fields.Char(string='Whatsapp Number')
    seminar_duplicate_id = fields.Many2one('seminar.leads', string='Seminar', ondelete='cascade')
    place = fields.Char(string='Place')
    admission_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Admission Status', readonly=True,
                                        default='no')
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other')],
                                string='District')
    email_address = fields.Char(string='Email Address')
    parent_number = fields.Char(string='Parent Number')
    preferred_course = fields.Many2one('logic.base.courses', string='Preferred Course')
    selected_lead = fields.Boolean(string='Selected Lead')

    @api.depends('incentive', 'student_name', 'selected_lead')
    def _total_incentive(self):
        ss = self.env['seminar.lead.incentive'].search([])
        for rec in ss:
            for i in self:
                if i.selected_lead == True:
                    i.incentive = rec.incentive_per_lead

    incentive = fields.Float(string='Incentive', compute='_total_incentive', store=True)
