from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Cliente, Pago
from django.db.models import Q
from django.http import Http404
from dateutil.relativedelta import relativedelta

from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from django.utils import timezone

def generar_reporte(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_quichinet_services.pdf"'
    
    clientes = Cliente.objects.all()
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    total_recibido = sum(pago.monto_pago for cliente in clientes for pago in cliente.pago_set.filter(fecha_pago_real__month=mes_actual, fecha_pago_real__year=año_actual))

    pdf = SimpleDocTemplate(response, pagesize=letter)
    elementos = []

    titulo = "Reporte de Pagos Empresa 'Quichinet Services'"
    estilo_titulo = ParagraphStyle(name='TitleStyle', fontSize=20, alignment=1, spaceAfter=20)
    elementos.append(Paragraph(titulo, estilo_titulo))
    elementos.append(Spacer(1, 12))

    fecha_actual = timezone.now().strftime("%d/%m/%Y")
    estilo_fecha = ParagraphStyle(name='DateStyle', fontSize=12, alignment=2)
    elementos.append(Paragraph(fecha_actual, estilo_fecha))
    elementos.append(Spacer(1, 12))

    tabla_datos = [["Nombre del Cliente", "Fecha de Pago Real", "Monto de Pago"]]
    for cliente in clientes:
        for pago in cliente.pago_set.filter(fecha_pago_real__month=mes_actual, fecha_pago_real__year=año_actual):
            fila = [cliente.nombre_cliente + " " + cliente.apellido_cliente, pago.fecha_pago_real, pago.monto_pago]
            tabla_datos.append(fila)

    tabla = Table(tabla_datos, colWidths=[180, 180, 180])
    estilo_tabla = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    tabla.setStyle(estilo_tabla)
    elementos.append(tabla)

    # Estilo para el total recibido
    estilo_total_recibido = ParagraphStyle(name='TotalRecibidoStyle', fontSize=16, textColor=colors.black, alignment=2)
    total_recibido_parrafo = Paragraph(f"Total Recibido: {total_recibido}", estilo_total_recibido)
    elementos.append(total_recibido_parrafo)

    pdf.build(elementos)
    return response

##################################################################################

@login_required
def eliminarPago(request, codigo):
    pago = Pago.objects.get(id_pago=codigo)
    pago.delete()
    return redirect("/informacionPago/" + str(pago.id_cliente.id_cliente))


@login_required
def cancelarPago(request, codigo):
    if request.method == "POST":
        fecha_real = request.POST["fecha_pago"]
        metodo_pago = request.POST["metodo_pago"]

        try:
            pago = Pago.objects.get(id_pago=codigo)
        except Pago.DoesNotExist:
            raise Http404("El Pago no existe")

        pago.fecha_pago_real = fecha_real
        pago.metodo_pago = metodo_pago
        pago.save()

        ################################################################
        codigo_cliente = str(pago.id_cliente.id_cliente)

        fecha_actual = pago.fecha_pago_esperada
        fecha_esperada_siguiente_mes = fecha_actual + relativedelta(months=1)

        monto_pago = pago.monto_pago

        try:
            cliente = Cliente.objects.get(id_cliente=codigo_cliente)
        except Cliente.DoesNotExist:
            raise Http404("El cliente no existe")

        cliente = Cliente.objects.get(id_cliente=codigo_cliente)

        nuevo_pago = Pago.objects.create(
            id_cliente=cliente,
            fecha_pago_esperada=fecha_esperada_siguiente_mes,
            monto_pago=monto_pago,
        )
        return redirect("/informacionPago/" + str(nuevo_pago.id_cliente.id_cliente))


##################################################################################


@login_required
def informacionPago(request, codigo):
    cliente = Cliente.objects.get(id_cliente=codigo)
    pagos = (
        Pago.objects.filter(Q(id_cliente_id=codigo))
        .order_by("-fecha_pago_esperada")
        .distinct()
    )
    context = {"pagos": pagos, "cliente": cliente}
    return render(request, "informacionPago.html", context)


##################################################################################


@login_required
def formPagoCliente(request, codigo):
    try:
        cliente = Cliente.objects.get(id_cliente=codigo)
    except Cliente.DoesNotExist:
        raise Http404("El cliente no existe")

    # Obtener el pago existente si está presente en la base de datos
    pago_existente = None
    if cliente.pago_set.exists():
        pago_existente = cliente.pago_set.first()

    # Determinar si es agregar o editar
    modo = "agregar" if not pago_existente else "editar"

    return render(request, "forms/agregarPago.html", {"cliente": cliente, "modo": modo, "pago_existente": pago_existente})


@login_required
def agregarPago(request):
    codigo_cliente = request.POST["codigo"]
    fecha_esperada = request.POST["fecha_esperada"]
    monto_pagar = request.POST["monto_pago"]

    try:
        cliente = Cliente.objects.get(id_cliente=codigo_cliente)
    except Cliente.DoesNotExist:
        raise Http404("El cliente no existe")

    pago = Pago.objects.create(
        id_cliente=cliente, fecha_pago_esperada=fecha_esperada, monto_pago=monto_pagar
    )
    return redirect("/informacionPago/" + codigo_cliente)

@login_required
def edicionPago(request, codigo):
    try:
        pago = Pago.objects.get(id_pago=codigo)
    except Cliente.DoesNotExist:
        raise Http404("El pago no existe")
    return render(request, "forms/edicionPago.html", {"pago": pago})


@login_required
def editarPago(request):
    if request.method == "POST":
        codigo = request.POST["codigo"]
        fecha_pago_esperada_var = request.POST["fecha_esperada"]
        monto_pago_var = request.POST["monto_pago"]

        try:
            pago = Pago.objects.get(id_pago=codigo)
        except Cliente.DoesNotExist:
            raise Http404("El cliente no existe")

        # Check if "fecha_real" key is in request.POST
        if "fecha_real" in request.POST:
            fecha_pago_real_var = request.POST["fecha_real"]
            pago.fecha_pago_real = fecha_pago_real_var

        if "metodo_pago" in request.POST:
            metodo_pago_var = request.POST["metodo_pago"]
            pago.metodo_pago = metodo_pago_var

        pago.fecha_pago_esperada = fecha_pago_esperada_var
        pago.monto_pago = monto_pago_var
        pago.save()

        return redirect("/informacionPago/" + str(pago.id_cliente.id_cliente))



##################################################################################
@never_cache
@login_required
def index(request):
    busqueda = request.GET.get("buscar")
    clientes = Cliente.objects.all().order_by('nombre_cliente')

    if busqueda:
        clientes = Cliente.objects.filter(
            Q(id_cliente__icontains=busqueda)
            | Q(nombre_cliente__icontains=busqueda)
            | Q(apellido_cliente__icontains=busqueda)
        ).distinct()

    usuario = request.user

    return render(request, "index.html", {"clientes": clientes, "usuario": usuario})


# CRUD
@login_required
def registrarCliente(request):
    nombre = request.POST["nombre"]
    apellido = request.POST["apellido"]
    dni = request.POST["dni"]
    direccion = request.POST["direccion"]
    telefonoC = request.POST["telefono"]
    fecha = request.POST["fecha"]
    equipo_var = request.POST["equipo"]
    ip_var = request.POST["ipv4"]
    red_var = request.POST["red"]

    cliente = Cliente.objects.create(
        nombre_cliente=nombre,
        apellido_cliente=apellido,
        dni_cliente=dni,
        direccion_cliente=direccion,
        telefono=telefonoC,
        fecha_conexion=fecha,
        equipo=equipo_var,
        ip=ip_var,
        red=red_var,
    )
    return redirect("/")


@login_required
def edicionCliente(request, codigo):
    try:
        cliente = Cliente.objects.get(id_cliente=codigo)
    except Cliente.DoesNotExist:
        raise Http404("El cliente no existe")
    return render(request, "forms/edicionCliente.html", {"cliente": cliente})


@login_required
def editarCliente(request):
    if request.method == "POST":
        codigo = request.POST["codigo"]
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        dni = request.POST["dni"]
        direccion = request.POST["direccion"]
        telefonoC = request.POST["telefono"]
        fecha = request.POST["fecha"]
        equipo_var = request.POST["equipo"]
        ip_var = request.POST["ipv4"]
        red_var = request.POST["red"]

        try:
            cliente = Cliente.objects.get(id_cliente=codigo)
        except Cliente.DoesNotExist:
            raise Http404("El cliente no existe")
        cliente.nombre_cliente = nombre
        cliente.apellido_cliente = apellido
        cliente.dni_cliente = dni
        cliente.direccion_cliente = direccion
        cliente.telefono = telefonoC
        cliente.fecha_conexion = fecha
        cliente.equipo = equipo_var
        cliente.ip = ip_var
        cliente.red = red_var
        cliente.save()

        return redirect("/")


@login_required
def eliminarCliente(request, codigo):
    cliente = Cliente.objects.get(id_cliente=codigo)
    cliente.delete()
    return redirect("/")


##################################################################################


@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                auth_login(request, form.get_user())
                return redirect("/")
        else:
            form = AuthenticationForm()
        return render(request, "registration/login.html", {"form": form})


def salir(request):
    logout(request)
    response = redirect("/")

    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
