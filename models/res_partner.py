from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    no_identitas = fields.Char(string='KTP No')
    nama_ayah = fields.Char(string="Father's Name")
    nama_ibu = fields.Char(string="Mother's Name")
    tmp_lahir = fields.Char(string='Place of Birth')
    tgl_lahir = fields.Date(string='Date of Birth')

#     yang belum
    bahasa = fields.Char(string="Language")
    pajak = fields.Char(string="Fax")
    judul = fields.Char(string="Title")

    # Aditional 
    pekerjaan = fields.Char(string="Job")
    

    gol_darah = fields.Selection([
        ('a','A'),
        ('b','B'),
        ('ab','AB'),
        ('o','O')], string='Blood Type')
    
    jenis_kelamin = fields.Selection([
        ('pria', 'Man'),
        ('wanita', 'Woman')], string='Gender')

    status_pernikahan = fields.Selection([
        ('belum', 'Single'),
        ('nikah', 'Married'),
        ('cerai', 'Divorce')], string='Marital Status')

    pendidikan = fields.Selection([
        ('sd', 'SD'),
        ('smp', 'SMP'),
        ('sma', 'SMA'),
        ('d3', 'D3'),
        ('s1', 'S1'),
        ('s2', 'S2'),
        ('s3', 'S3')], 
        string='Educational')
    

    age_days = fields.Integer( 
        string='Umur', 
        compute='_compute_age', 
        inverse='_inverse_age', 
        search='_search_age', 
        store=False, # optional
        compute_sudo=True, # optional 
        readonly=True,
    )

    @api.depends('tgl_lahir')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.tgl_lahir:
                delta = today - book.tgl_lahir
                book.age_days = int(delta.days/365)
            else:
                book.age_days = 0
    
    @api.constrains('tgl_lahir')
    def _check_tgl(self): 
        tanggal_lahir = self.tgl_lahir
        if tanggal_lahir and tanggal_lahir > fields.Date.today(): 
            raise models.ValidationError( 'Error! tanggal lahir tidagld.')