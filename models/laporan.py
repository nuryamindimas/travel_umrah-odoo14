import base64
import xlsxwriter

from odoo import models, fields, api, _
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO

class cetak_excel(models.TransientModel):
    _name = "cetak.excel"
    _description = "cetak excel"
    paket_peserta_line = fields.Many2one(
            comodel_name='paket.peserta.line',
            string='Package ',
    )

    name = fields.Char(string='Name', default="PRODUCT LIST")
    filename = fields.Char(string='Filename')
    data_file = fields.Binary(string='Data file')
    date_created = fields.Date(string='Date Created', default=fields.Date.today())

    def export(self):
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


        


        ws.merge_range('A1:D1',  self.name + ' ' + str(self.date_created), style_bold)
        ws.set_column(1, 1, 10)
        ws.set_column(1, 2, 40)
        ws.set_column(1, 3, 25)
        ws.set_column(1, 4, 25)
        
        ws.write(3, 0,'NO ', style_bold_orange)
        ws.write(3, 1,'TITLE ', style_bold_orange)
        ws.write(3, 2, 'GENDER', style_bold_orange)
        ws.write(3, 3, 'FULL NAME ', style_bold_orange)
        ws.write(3, 3, 'TEMPAT LAHIR ', style_bold_orange)
        ws.write(3, 3, 'TANGGAL LAHIR ', style_bold_orange)
        ws.write(3, 3, 'NO PASSPORT ', style_bold_orange)
        ws.write(3, 3, 'PASSPORT ISSUED', style_bold_orange)
        ws.write(3, 3, 'PASSPORT EXPIRED ', style_bold_orange)
        ws.write(3, 3, 'IMIGRASI ', style_bold_orange)
        ws.write(3, 3, 'MAHRAM', style_bold_orange)
        ws.write(3, 3, 'USIA', style_bold_orange)
        ws.write(3, 3, 'NIK ', style_bold_orange)

        row_count = 4
        count = 1

        for peserta in self.peserta_line.partner_id:
            ws.write(row_count, 0, str(count), style_no_bold)
            ws.write(row_count, 1,peserta.title, style_no_bold)
            ws.write(row_count, 2,peserta.jenis_kelamin, style_no_bold)
            ws.write(row_count, 3,peserta.name, style_no_bold)
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
            'res_model': 'cetak.excel',
            'views': [(view.id, 'form')],
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            }    


