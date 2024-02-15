from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .models import Cliente, Pago
from django.db.models import Q
from django.http import Http404
from dateutil.relativedelta import relativedelta

# Create your views here.


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
    return render(request, "forms/agregarPago.html", {"cliente": cliente})


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
