function validarDecimal(input) {
    input.value = input.value.replace(/[^0-9.]/g, '');
    const partes = input.value.split('.');
    if (partes.length > 2) {
        input.value = partes[0] + '.' + partes.slice(1).join('');
    }
    const indexPunto = input.value.indexOf('.');
    if (indexPunto !== -1 && input.value.length - indexPunto > 3) {
        input.value = input.value.substring(0, indexPunto + 3);
    }
}

$(document).ready(function () {
    function calcularFechaSiguienteMes() {
        const fechaActual = new Date();
        const diaActual = fechaActual.getDate();
        let mesSiguiente = fechaActual.getMonth() + 1;
        let anioSiguiente = fechaActual.getFullYear();

        if (mesSiguiente === 12) {
            mesSiguiente = 0;
            anioSiguiente++;
        }
        const fechaSiguienteMes = new Date(anioSiguiente, mesSiguiente, diaActual);
        const fechaFormateada = fechaSiguienteMes.toISOString().split('T')[0];
        $('#fecha_esperada').val(fechaFormateada);
    }
    calcularFechaSiguienteMes();
});