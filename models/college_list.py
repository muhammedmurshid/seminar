from odoo import api, fields, models, _


class CollegeList(models.Model):
    _name = 'college.list'
    _description = 'College'
    _rec_name = 'college_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    college_name = fields.Char(string='Institute Name', required=True, copy=False)
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other')],

                                string='District', required=True)
    type = fields.Selection([('school', 'School'), ('college', 'College')], string='Type')
    place = fields.Char(string='Place', required=True)
    contact_number = fields.Char(string='Contact Number', required=True)
    first_year = fields.Boolean(string='First Year')
    second_year = fields.Boolean(string='Second Year')
    third_year = fields.Boolean(string='Third Year')
    school_type = fields.Selection([('hse', 'HSE'), ('hs', 'HS')], string='School Type')
    designation = fields.Char(string='Designation')
    contact_person_name = fields.Char(string='Contact Person Name')
    institute_number = fields.Char(string='Institute Number')


