$(document).ready(function () {
    $('.eliminar-pago').on('click', function (event) {
        event.preventDefault();

        var pagoId = $(this).data('pago-id');
        var urlBase = $(this).data('eliminar-url');
        var url = urlBase.replace('0', pagoId);

        var confirmarEliminar = confirm('¿Estás seguro de que deseas eliminar este pago?');

        if (confirmarEliminar) {
            window.location.href = url;
        }
    });
    $('[id^=fecha_pago_]').val(new Date().toISOString().substr(0, 10));

    $('.mostrar-formulario').on('click', function (event) {
        event.preventDefault();
        var pagoId = $(this).data('pago-id');
        $('#formulario' + pagoId).toggle();
    });
});