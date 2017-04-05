import xlwt


def set_style(bold=False, horz_center=True):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = 'Arial'
    font.bold = bold
    font.color_index = 4
    font.height = 220
    style.font = font
    al = xlwt.Alignment()
    if horz_center:
        al.horz = xlwt.Alignment.HORZ_CENTER
    else:
        al.horz = xlwt.Alignment.HORZ_LEFT
    al.vert = xlwt.Alignment.VERT_CENTER
    al.wrap = xlwt.Alignment.WRAP_AT_RIGHT
    style.alignment = al
    return style
