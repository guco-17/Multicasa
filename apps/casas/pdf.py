import textwrap
from django.utils import timezone


def _pdf_escape(text: str) -> bytes:
    """Encode text in cp1252 (WinAnsiEncoding) and escape PDF string delimiters."""
    normalized = (
        str(text)
        .replace('\\', '\\\\')
        .replace('(', '\\(')
        .replace(')', '\\)')
        .replace('\r', ' ')
        .replace('\n', ' ')
    )
    return normalized.encode('cp1252', errors='replace')


def build_casa_ficha_pdf(casa) -> bytes:
    """
    Generate a formatted PDF technical data sheet (Ficha Técnica) for a Casa instance
    using standard PDF 1.4 primitives and WinAnsiEncoding (cp1252) for Spanish accents.
    """
    streams = []

    def add_cmd(cmd: str):
        streams.append(cmd.encode('ascii'))

    def add_text(x: float, y: float, text: str, font: str = 'F1', size: int = 11, color: tuple = (0.19, 0.24, 0.27)):
        r, g, b = color
        escaped = _pdf_escape(text)
        streams.append(
            f'BT /{font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg 1 0 0 1 {x:.1f} {y:.1f} Tm ('.encode('ascii')
            + escaped
            + b') Tj ET'
        )

    def add_rect(x: float, y: float, w: float, h: float, fill_rgb: tuple = None, stroke_rgb: tuple = None):
        ops = []
        if fill_rgb is not None:
             ops.append(f'{fill_rgb[0]:.3f} {fill_rgb[1]:.3f} {fill_rgb[2]:.3f} rg')
        if stroke_rgb is not None:
            ops.append(f'{stroke_rgb[0]:.3f} {stroke_rgb[1]:.3f} {stroke_rgb[2]:.3f} RG 1 w')
        ops.append(f'{x:.1f} {y:.1f} {w:.1f} {h:.1f} re')
        if fill_rgb is not None and stroke_rgb is not None:
            ops.append('B')
        elif fill_rgb is not None:
            ops.append('f')
        else:
            ops.append('S')
        add_cmd(' '.join(ops))

    # Header banner
    add_rect(40, 725, 532, 65, fill_rgb=(0.071, 0.247, 0.361))
    add_text(56, 762, 'BIENES RAÍCES MULTICASA', font='F2', size=16, color=(1, 1, 1))
    add_text(56, 742, 'Ficha Técnica de Propiedad Inmobiliaria', font='F1', size=11, color=(0.82, 0.91, 0.96))

    estatus_label = casa.get_estatus_display()
    add_text(440, 762, f'Folio #{casa.pk}', font='F2', size=12, color=(1, 1, 1))
    add_text(440, 742, f'Estatus: {estatus_label}', font='F1', size=10, color=(0.90, 0.96, 0.85))

    # Title and Price box
    add_rect(40, 650, 532, 62, fill_rgb=(0.969, 0.980, 0.984), stroke_rgb=(0.835, 0.890, 0.914))
    titulo_lines = textwrap.wrap(casa.titulo, width=52) or [casa.titulo]
    add_text(54, 690, titulo_lines[0], font='F2', size=15, color=(0.071, 0.247, 0.361))
    ubicacion_texto = f'{casa.direccion}, {casa.ciudad} - Zona {casa.zona}'
    add_text(54, 668, ubicacion_texto[:85], font='F1', size=10, color=(0.408, 0.467, 0.494))

    precio_str = f'${casa.precio:,.2f} MXN'
    add_text(410, 690, 'PRECIO', font='F2', size=9, color=(0.408, 0.467, 0.494))
    add_text(410, 670, precio_str, font='F2', size=14, color=(0.294, 0.475, 0.114))

    # Technical Specifications Table
    add_text(40, 622, 'CARACTERÍSTICAS Y DATOS TÉCNICOS', font='F2', size=12, color=(0.071, 0.247, 0.361))
    add_rect(40, 616, 532, 1.5, fill_rgb=(0.098, 0.643, 0.816))

    fecha_str = (
        timezone.localtime(casa.fecha_registro).strftime('%d/%m/%Y %H:%M')
        if casa.fecha_registro
        else 'N/D'
    )
    specs = [
        ('ID de registro', str(casa.pk), 'Estatus', estatus_label),
        ('Ciudad', casa.ciudad, 'Zona', casa.zona),
        ('Recámaras', str(casa.recamaras), 'Baños', str(casa.banos)),
        ('Construcción', f'{casa.metros_construccion} m2', 'Terreno', f'{casa.metros_terreno} m2'),
        ('Latitud', str(casa.latitud), 'Longitud', str(casa.longitud)),
        ('Fecha de registro', fecha_str, 'Precio de lista', f'${casa.precio}'),
    ]

    y_row = 588
    for idx, (label1, val1, label2, val2) in enumerate(specs):
        bg = (0.961, 0.976, 0.980) if idx % 2 == 0 else (1.0, 1.0, 1.0)
        add_rect(40, y_row - 8, 532, 26, fill_rgb=bg, stroke_rgb=(0.863, 0.906, 0.922))
        add_text(52, y_row, f'{label1}:', font='F2', size=10, color=(0.408, 0.467, 0.494))
        add_text(155, y_row, val1, font='F1', size=10, color=(0.188, 0.243, 0.271))
        add_text(310, y_row, f'{label2}:', font='F2', size=10, color=(0.408, 0.467, 0.494))
        add_text(415, y_row, val2, font='F1', size=10, color=(0.188, 0.243, 0.271))
        y_row -= 26

    # Address row
    add_rect(40, y_row - 8, 532, 26, fill_rgb=(0.961, 0.976, 0.980), stroke_rgb=(0.863, 0.906, 0.922))
    add_text(52, y_row, 'Dirección:', font='F2', size=10, color=(0.408, 0.467, 0.494))
    add_text(155, y_row, casa.direccion[:75], font='F1', size=10, color=(0.188, 0.243, 0.271))
    y_row -= 44

    # Description section
    add_text(40, y_row, 'DESCRIPCIÓN DE LA PROPIEDAD', font='F2', size=12, color=(0.071, 0.247, 0.361))
    add_rect(40, y_row - 6, 532, 1.5, fill_rgb=(0.098, 0.643, 0.816))

    desc_lines = []
    for paragraph in (casa.descripcion or '').splitlines():
        wrapped = textwrap.wrap(paragraph.strip(), width=82)
        desc_lines.extend(wrapped if wrapped else [''])
    if not desc_lines:
        desc_lines = ['Sin descripción registrada.']

    desc_lines = desc_lines[:14]
    box_height = max(60, len(desc_lines) * 16 + 24)
    box_bottom = y_row - 16 - box_height
    add_rect(40, box_bottom, 532, box_height, fill_rgb=(1, 1, 1), stroke_rgb=(0.863, 0.906, 0.922))

    text_y = y_row - 34
    for line in desc_lines:
        if line:
            add_text(52, text_y, line, font='F1', size=10, color=(0.224, 0.294, 0.333))
        text_y -= 16

    # Footer
    add_rect(40, 48, 532, 1, fill_rgb=(0.835, 0.890, 0.914))
    add_text(
        40,
        32,
        'Bienes Raíces Multicasa - Documento informativo generado automáticamente.',
        font='F1',
        size=9,
        color=(0.45, 0.51, 0.55),
    )

    content_stream = b'\n'.join(streams)

    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        (
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] '
            b'/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> '
            b'/Contents 6 0 R >>'
        ),
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
        b'<< /Length ' + str(len(content_stream)).encode('ascii') + b' >>\nstream\n' + content_stream + b'\nendstream',
    ]

    pdf = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f'{index} 0 obj\n'.encode('ascii'))
        pdf.extend(obj)
        pdf.extend(b'\nendobj\n')

    xref_offset = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets[1:]:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode('ascii'))

    pdf.extend(
        f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n'.encode('ascii')
    )
    return bytes(pdf)
