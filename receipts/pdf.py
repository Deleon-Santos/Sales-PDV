from io import BytesIO
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def build_receipt_pdf(sale):
    buffer = BytesIO()
    width = 80 * mm
    height = max(90, 35 + len(sale.items.all()) * 12 + 70) * mm
    pdf = canvas.Canvas(buffer, pagesize=(width, height))

    y = height - 10 * mm
    left = 5 * mm

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(width / 2, y, "SUPERMERCADO")
    y -= 5 * mm

    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(width / 2, y, "CUPOM DE VENDA")
    y -= 6 * mm

    pdf.drawString(left, y, f"Venda: #{sale.id}")
    y -= 4 * mm
    pdf.drawString(left, y, f"Caixa: {sale.cashier.username}")
    y -= 4 * mm
    pdf.drawString(left, y, sale.created_at.strftime("%d/%m/%Y %H:%M"))
    y -= 6 * mm

    pdf.line(left, y, width - left, y)
    y -= 5 * mm

    for item in sale.items.select_related("product").all():
        name = item.product.name[:25]
        pdf.drawString(left, y, name)
        y -= 3.5 * mm
        pdf.drawString(left, y, f"{item.quantity} x R$ {item.unit_price:.2f}")
        pdf.drawRightString(width - left, y, f"R$ {item.subtotal:.2f}")
        y -= 5 * mm

    pdf.line(left, y, width - left, y)
    y -= 6 * mm

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(left, y, "TOTAL")
    pdf.drawRightString(width - left, y, f"R$ {sale.total:.2f}")
    y -= 5 * mm

    pdf.setFont("Helvetica", 7)
    pdf.drawString(left, y, f"Pagamento: {sale.get_payment_method_display()}")
    y -= 8 * mm
    pdf.drawCentredString(width / 2, y, "Obrigado pela preferência!")

    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="cupom-venda-{sale.id}.pdf"'
    return response
