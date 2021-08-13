# -*- coding: utf-8 -*-
import base64
import xlsxwriter

from odoo import models, fields, api, _
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO



class paket_perjalanan(models.Model):
    _name = "paket.perjalanan"
    
    name = fields.Char(string='Reference', readonly=True, default='/')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    tgl_berangkat = fields.Date(string='Departure Date', required=True)
    tgl_pulang = fields.Date(string='Return Date', required=True)
    quota = fields.Integer(string='Quota')
    quota_progress = fields.Float(string="Quota Progress", compute='_taken_seats')
    note = fields.Text(string='Notes')
    hotel_line = fields.One2many('paket.hotel.line', 'paket_perjalanan_id', string='Hotel Lines')
    pesawat_line = fields.One2many('paket.pesawat.line', 'paket_perjalanan_id', string='Airline Lines')
    acara_line = fields.One2many('paket.acara.line', 'paket_perjalanan_id', string='Schedule Lines')
    peserta_line = fields.One2many('paket.peserta.line', 'paket_perjalanan_id', string='Jamaah Lines', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),], 
        string='Status', 
        readonly=True, 
        copy=False, 
        default='draft', 
        track_visibility='onchange')
    # sale_order_id = fields.One2many(comodel_name='sale.order', inverse_name='paket_perjalanan_id', string='order')
        
    filename = fields.Char(string='Filename')
    data_file = fields.Binary(string='Data file')
    date_created = fields.Date(string='Date Created', default=fields.Date.today())

    
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('paket.perjalanan')
        return super(paket_perjalanan, self).create(vals)
    
    
    def name_get(self):
        return [(this.id, this.name + "#" + " " + this.product_id.partner_ref) for this in self]
    
    @api.depends('quota', 'peserta_line')
    def _taken_seats(self):
        for r in self:
            if not r.quota:
                r.quota_progress = 0.0
            else:
                r.quota_progress = 100.0 * len(r.peserta_line) / r.quota
    
    def update_jamaah(self):
        order_ids =self.env['sale.order'].search([('paket_perjalanan_id', '=', self.id), ('state', 'not in', ('draft', 'cancel'))])
        if order_ids:
            self.peserta_line.unlink()
            for o in order_ids:
                for x in o.passport_line:
                    self.peserta_line.create({
                        'paket_perjalanan_id' : self.id,
                        'partner_id' : x.partner_id.id,
                        'name' : x.name,
                        'order_id' : o.id,
                        'jenis_kelamin' : x.partner_id.jenis_kelamin,
                        'tipe_kamar' : x.tipe_kamar,
                    })
    
    def cetak_jamaah_xls(self):
        folder_title = self.name + "-" + str(self.date_created) + ".xlsx"
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        ws = workbook.add_worksheet((self.name))

        style = workbook.add_format({'left': 1, 'top': 1,'right':1,'bold': True,'fg_color': '#339966','font_color': 'white','align':'center'})
        style.set_text_wrap()
        style.set_align('vcenter')
        style_bold = workbook.add_format({'left': 1, 'top': 1,'right':1,'bottom':1,'bold': True,'align':'center','num_format':'_(Rp* #,##0_);_(Rp* (#,##0);_(* "-"??_);_(@_)'})
        style_bold_orange = workbook.add_format({'left': 1, 'top': 1,'right':1,'bold': True,'align':'center','fg_color': '#FF6600','font_color': 'white'})
        style_no_bold = workbook.add_format({'left': 1,'right':1,'bottom':1, 'num_format':'_(Rp* #,##0_);_(Rp* (#,##0);_(* "-"??_);_(@_)'})

        style_umur = workbook.add_format({'left': 1,'right':1,'bottom':1, 'num_format':''})
        style_date = workbook.add_format({'left': 1,'right':1,'bottom':1, 'num_format':'dd/mm/yy'})


        


        ws.merge_range('A1:D1',  self.name + ' ' + str(self.date_created), style_bold)
        ws.set_column(1, 1, 10)
        ws.set_column(1, 2, 40)
        ws.set_column(1, 3, 25)
        ws.set_column(1, 4, 25)

        
        
        ws.write(3, 0,'NO ', style_bold_orange)
        ws.write(3, 1,'TITLE ', style_bold_orange)
        ws.write(3, 2, 'GENDER', style_bold_orange)
        ws.write(3, 3, 'FULL NAME ', style_bold_orange)
        ws.write(3, 4, 'TEMPAT LAHIR ', style_bold_orange)
        ws.write(3, 5, 'TANGGAL LAHIR ', style_bold_orange)
        ws.write(3, 6, 'NO PASSPORT ', style_bold_orange)
        ws.write(3, 7, 'PASSPORT ISSUED', style_bold_orange)
        ws.write(3, 8, 'PASSPORT EXPIRED ', style_bold_orange)
        ws.write(3, 9, 'IMIGRASI ', style_bold_orange)
        ws.write(3, 10, 'MAHRAM', style_bold_orange)
        ws.write(3, 11, 'USIA', style_bold_orange)
        ws.write(3, 12, 'NIK ', style_bold_orange)
        ws.write(3, 13, 'Order ', style_bold_orange)
        ws.write(3, 14, 'Room Type ', style_bold_orange)
        ws.write(3, 15, 'Room Leader', style_bold_orange)
        ws.write(3, 16, 'Room No ', style_bold_orange)
        ws.write(3, 17, 'Alamat ', style_bold_orange)

        row_count = 4
        count = 1

        for peserta in self.peserta_line:
            ws.write(row_count, 0, str(count), style_no_bold)
            ws.write(row_count, 1,peserta.partner_id.title.name, style_no_bold)
            ws.write(row_count, 2,peserta.partner_id.jenis_kelamin, style_no_bold)
            ws.write(row_count, 3,peserta.partner_id.name, style_no_bold)
            ws.write(row_count, 4,peserta.partner_id.tmp_lahir, style_no_bold)
            ws.write(row_count, 5,peserta.partner_id.tgl_lahir, style_date)
            ws.write(row_count, 6,peserta.order_id.passport_line.nomor, style_no_bold)
            ws.write(row_count, 7,peserta.order_id.date_order, style_date)
            ws.write(row_count, 8,peserta.order_id.passport_line.masa_berlaku, style_date)
            ws.write(row_count, 9,self.hotel_line.partner_id.city, style_no_bold)
            ws.write(row_count, 10,peserta.partner_id.name, style_no_bold)
            ws.write(row_count, 11,peserta.partner_id.age_days, style_umur)
            ws.write(row_count, 12,peserta.partner_id.no_identitas, style_no_bold)
            ws.write(row_count, 13,peserta.order_id.name, style_no_bold)
            ws.write(row_count, 14,peserta.order_id.passport_line.tipe_kamar, style_no_bold)
            ws.write(row_count, 15,"-", style_no_bold)
            ws.write(row_count, 16,"-", style_no_bold)
            ws.write(row_count, 17,peserta.partner_id.street, style_no_bold)
            
            count+=1
            row_count+=1
        
        row_count+=2
        count = 1
        ws.write(row_count, 2,'NO ', style_bold_orange)
        ws.write(row_count, 3,'AIRLINES ', style_bold_orange)
        ws.write(row_count, 4, 'DEPARTURE DATE', style_bold_orange)
        ws.write(row_count, 5, 'DEPARTURE CITY', style_bold_orange)
        ws.write(row_count, 6, 'ARIVAL CITY', style_bold_orange)
        row_count+=1

        for  pesawat in self.pesawat_line:
            ws.write(row_count, 2, str(count), style_no_bold)
            ws.write(row_count, 3, pesawat.partner_id.name, style_no_bold)
            ws.write(row_count, 4, pesawat.tgl_berangkat, style_date)
            ws.write(row_count, 5, pesawat.kota_asal, style_no_bold)
            ws.write(row_count, 6, pesawat.kota_tujuan, style_no_bold)
            count+=1
            row_count+=1

        workbook.close()        
        out = base64.encodestring(file_data.getvalue())
        self.write({'data_file': out, 'filename': folder_title})

        return self.view_form()

    def view_form(self):
        view = self.env.ref('travel_umroh.view_report_excel')
        return {
            'name': _('Cetak Excel'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'paket.perjalanan',
            'views': [(view.id, 'form')],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            }

        

class paket_hotel_line(models.Model):
    _name = "paket.hotel.line"
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Hotel', required=True)
    tgl_awal = fields.Date(string='Start Date', required=True)
    tgl_akhir = fields.Date(string='End Date', required=True)
    kota = fields.Char(related='partner_id.city', string='City', readonly=True)
 
class paket_pesawat_line(models.Model):
    _name = "paket.pesawat.line"
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Airlines', required=True)
    tgl_berangkat = fields.Date(string='Departure Date', required=True)
    kota_asal = fields.Char(string='Departure City', required=True)
    kota_tujuan = fields.Char('Arrival City', required=True)
 
class paket_acara_line(models.Model):
    _name = "paket.acara.line"
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    name = fields.Char(string='Name', required=True)
    tgl = fields.Date(string='Date', required=True)
 
class paket_peserta_line(models.Model):
    _name = "paket.peserta.line"
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Jamaah')
    name = fields.Char(string='Name in Passport')
    order_id = fields.Many2one('sale.order', string='Sales Orders')
    jenis_kelamin = fields.Selection([('pria', 'Man'), ('wanita', 'Woman')], string='Gender')
    tipe_kamar = fields.Selection([('d', 'Double'), ('t', 'Triple'), ('q', 'Quad')], string='Room Type')

class sale_order(models.Model):
    _inherit = "sale.order"
    
    paket_perjalanan_id = fields.Many2one('paket.perjalanan', string='Paket Perjalanan', domain=[('state', '=', 'confirm')])
    dokumen_line = fields.One2many('sale.dokumen.line', 'order_id', string='Document Lines')
    passport_line = fields.One2many('sale.passport.line', 'order_id', string='Passport Lines')
    
    @api.onchange('paket_perjalanan_id')
    def set_order_line(self):
        # res = {}
        if self.paket_perjalanan_id:
            pp = self.paket_perjalanan_id    

           
            
            order = self.env['sale.order'].new({    
                'partner_id': self.partner_id.id,
                'pricelist_id': self.pricelist_id.id,
                'date_order': self.date_order
            })
            line = self.env['sale.order.line'].new({
                'product_id': pp.product_id.id, 
                'order_id': order.id})
            line.product_id_change()
            self.order_line = line
            
            # vals = line._convert_to_write({name: line[name] for name in line._cache})
            # res['value'] = {'order_line': [vals]}
             
            # res['value'] = {
            #     'order_line': [{
            #         # 'order_id' : 1,
            #         'product_id': pp.product_id.id,
            #         'name':  pp.product_id.partner_ref,
            #         'product_uom_qty': 1,
            #         'product_uom': pp.product_id.uom_id.id,
            #         'price_unit': pp.product_id.lst_price
            #     }]
            # }
            
   

  
    
    class sale_dokumen_line(models.Model):
        _name = "sale.dokumen.line"
        
        order_id = fields.Many2one('sale.order', string='Sales Orders', ondelete='cascade')
        name = fields.Char(string='Name', required=True)
        foto = fields.Binary(string='Photo', required=True)


    class sale_passport_line(models.Model):
        _name = "sale.passport.line"
        
        order_id = fields.Many2one('sale.order', string='Sales Orders', ondelete='cascade')
        partner_id = fields.Many2one('res.partner', string='Jamaah', required=True)
        nomor = fields.Char(string='Passport Number', required=True)
        name = fields.Char(string='Name in Passport', required=True)
        masa_berlaku = fields.Date(string='Date of Expiry', required=True)
        tipe_kamar = fields.Selection([('d', 'Double'), ('t', 'Triple'), ('q', 'Quad')], string='Room Type', required=True)
        foto = fields.Binary(string='Photo', required=True)




