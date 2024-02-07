$(document).ready(function () {
  $(".eliminar-cliente").click(function (event) {
    event.preventDefault();

    var clienteId = $(this).data("cliente-id");
    var eliminarUrl = $(this).data("eliminar-url");
    var confirmarEliminar = confirm(
      "¿Estás seguro de que deseas eliminar este cliente?"
    );

    if (confirmarEliminar) {
      window.location.href = eliminarUrl.replace("0", clienteId);
    }
  });

  $("#fecha").val(new Date().toISOString().substr(0, 10));

  $("#mostrarFormulario").click(function () {
    $("#formularioContainer").css("display", "flex");
  });
});

function cerrarFormulario() {
  $("#formularioContainer").css("display", "none");
}
