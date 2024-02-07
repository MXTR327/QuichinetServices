from django.contrib import admin
from django.urls import path, include
from gestionClientes import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index),
    path("registrarCliente/", views.registrarCliente),
    path("eliminarCliente/<codigo>", views.eliminarCliente, name="eliminarCliente"),
    path("edicionCliente/<codigo>", views.edicionCliente, name="edicionCliente"),
    path("editarCliente/", views.editarCliente),
    path("formPago/<codigo>", views.formPagoCliente, name="formAgregarPago"),
    path("agregarPago/", views.agregarPago, name="agregarPago"),
    path("informacionPago/<codigo>", views.informacionPago, name="informacionPago"),
    path("cancelarPago/<codigo>", views.cancelarPago, name="cancelarPago"),
    path("eliminarPago/<codigo>", views.eliminarPago, name="eliminarPago"),
    path("login/", views.login),
    path("accounts/login/", views.login),
    path("salir/", views.salir, name="salir"),
    path("index/", views.index, name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
]
