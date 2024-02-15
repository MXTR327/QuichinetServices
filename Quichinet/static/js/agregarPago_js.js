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
    $("#fecha_esperada").val(new Date().toISOString().substr(0, 10));
});
