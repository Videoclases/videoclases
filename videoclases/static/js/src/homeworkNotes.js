
function ViewModel() {
    let self = this;
    self.loading = ko.observable(true);
    self.dataEvaluations = ko.observableArray([]);
    self.dataHeaders = ko.observableArray([]);
    self.teacherEvaluations = ko.observable();
}

let vm = new ViewModel();

let format = function (d) {
    // `d` is the original data object for the row
    let body = '';
    body += '<tr>' +
        '<th colspan="2"><h4>Datos del video</h4> </th>' +
        '</tr>';
    if (d.videoclase && d.videoclase.url) {
        body += '<tr>' +
            '<th>Url Youtube: </th>' +
            '<td>' + d.videoclase.url + '</td>' +
            '</tr>' +
            '<tr>' +
            '<th>Fecha de subida: </th>' +
            '<td>' + d.videoclase.date + '</td>' +
            '</tr>' +
            '<tr>' +
            '<th>Pregunta: </th>' +
            '<td>' + d.videoclase.question + '</td>' +
            '</tr>' +
            '<tr>' +
            '<th>Respuesta: </th>' +
            '<td>' + d.videoclase.response + '</td>' +
            '</tr>'
    } else {
        body += '<tr>' +
            '<th>Video: </th>' +
            '<td>No se subió url de video</td>' +
            '</tr>'
    }

    body += '<tr>' +
        '<th colspan="2"><h4>Evaluaciones</h4> </th>' +
        '</tr>';
    if (d.empty || d.criterias[0].empty) {
        body += '<tr>' +
            '<td colspan="2">No registra evaluaciones de sus compañeros</td>' +
            '</tr>'
    } else {
        d.criterias.forEach(c => {
            body += '<tr>' +
                '<th>' + c.name + ': </th>' +
                '<td><table class="table"><tr>' +
                '  <th>Promedio</th>' +
                `<td>${c.avg}</td></tr>` +
                '<tr>  <th>Nota máxima</th>' +
                `<td>${c.max_score}</td></tr>` +
                '  <tr><th>Nota mínima</th>' +
                `<td>${c.min_score}</td></tr>` +
                '  <tr><th>Cantidad de evaluaciones</th>' +
                `<td>${c.number_evaluations}</td></tr>` +
                '  <tr><th>Evaluaciones filtradas</th>' +
                `<td>0 (not working yet)</td></tr>` + // TODO: change this later
                '  <tr><th>Moda</th>' +
                `<td>${c.mode}</td></tr>` +
                '  <tr><th>Desviación estandar</th>' +
                `<td>${c.standar_desv}</td></tr>` +
                '  <tr><th>Varianza</th>' +
                `<td>${c.variance}</td>` +
                '</tr></table></td>' +
                '</tr>'
        });
    }

    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;" class="table table-responsive">' +
        '<tr>' +
        '<th colspan="2"><h4>Datos del Alumno</h4> </th>' +
        '</tr>' +
        '<tr>' +
        '<th>Nombre Completo: </th>' +
        `<td>${d.student.first_name} ${d.student.last_name}</td>` +
        '</tr>' + body +
        '</table>';

};

$(document).ready(function() {
    ko.applyBindings(vm);
    $.ajax( {
        "dataType": 'json',
        "type": "POST",
        "url": homework_url,
        "beforeSend": function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        "success":function (result) {
            $(".loader").fadeOut();
            console.log(JSON.stringify(result));
            vm.dataHeaders(result.headers);
            vm.dataEvaluations(result.evaluations);
            vm.teacherEvaluations(result.teacherEvaluations);
            let dt = $('#table').DataTable({
                "language" : {
                    url: i18n_url
                },
                dom: 'Bfrtip',
                pageLength: 50,
                buttons: [
                    {
                        extend:'copy',
                        text:'Copiar',
                    },
                    {
                        extend:'excel',
                    },
                    {
                        extend:'pdf',
                    },
                    {
                        extend:'print',
                        text:'Imprimir',
                    },
                ],
                //          "columns": [
                //     {
                //         "class":          "details-control",
                //         "orderable":      false,
                //         "defaultContent": ""
                //     },
                // ],
                columnDefs: [
                    {
                        targets: 'details-control', orderable: false,
                        "defaultContent": ""
                    }
                ],
                "order": [[2, 'asc']]

            } );


            $('#table tbody').on('click', 'tr td.details-control', function () {
                let tr = $(this).closest('tr');
                let row = dt.row(tr);
                let idx = tr.attr('id');

                if (row.child.isShown()) {
                    tr.find('i').removeClass('fa-minus-circle text-danger');
                    tr.find('i').addClass('fa-plus-circle text-success');
                    row.child.hide();
                }
                else {
                    tr.find('i').removeClass('fa-plus-circle text-success');
                    tr.find('i').addClass('fa-minus-circle text-danger');
                    row.child(format(vm.dataEvaluations()[idx]), 'new-row').show();
                }
            });

        }
    } );

});