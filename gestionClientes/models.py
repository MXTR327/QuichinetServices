from django.db import models

# Create your models here.


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre_cliente = models.CharField(max_length=50, null=False)
    apellido_cliente = models.CharField(max_length=50, null=False)
    dni_cliente = models.CharField(max_length=50, null=False)
    direccion_cliente = models.CharField(max_length=50, null=False)
    telefono = models.CharField(max_length=50, null=False)
    fecha_conexion = models.DateField(null=False)


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pago_esperada = models.DateField(null=False)
    fecha_pago_real = models.DateField(null=True)
    monto_pago = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    metodo_pago = models.CharField(max_length=50, null=True)
