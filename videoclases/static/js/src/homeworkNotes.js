
function ViewModel() {
    let self = this;
    self.loading = ko.observable(true);
    self.dataEvaluations = ko.observableArray([]);
    self.dataEvaluationsTeacher = ko.observableArray([]);
    self.dataHeaders = ko.observableArray([]);
    self.teacherEvaluations = ko.observable();

    self.evaluateVideoclase = function (data) {
        location.href = teacher_evaluate_url + '?id=' + data.videoclase_id;
    }
}

let vm = new ViewModel();

const formatBaseBody = function (d) {
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
    if (d.empty || !d.criterias[0].avg) {
        body += '<tr>' +
            '<td colspan="2">No registra evaluaciones</td>' +
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
    return body
};

const formatStudent = function (d) {
    // `d` is the original data object for the row

    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;" class="table table-responsive">' +
        '<tr>' +
        '<th colspan="2"><h4>Datos del Alumno</h4> </th>' +
        '</tr>' +
        '<tr>' +
        '<th>Nombre Completo: </th>' +
        `<td>${d.student.first_name} ${d.student.last_name}</td>` +
        '</tr>' + formatBaseBody(d) +
        '</table>';

};
const formatTeacher = function (d) {
    // `d` is the original data object for the row
    let studentsBody = "<ul class=\"list-unstyled\">";
    d.students.forEach(s => studentsBody += `<li>${s.first_name} ${s.last_name}</li>`);
    studentsBody += "</ul>";
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;" class="table table-responsive">' +
        '<tr>' +
        '<th colspan="2"><h4>Datos del grupo</h4> </th>' +
        '</tr>' +
        '<tr>' +
        '<th>Nombre estudiantes: </th>' +
        `<td>${studentsBody}</td>` +
        '</tr>' + formatBaseBody(d) +
        '</table>';

};

const sendAjax = function (url, onSucess, onError = (error) => {
    console.log(error)
}) {
    $.ajax( {
        "dataType": 'json',
        "type": "POST",
        "url": url,
        "beforeSend": function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        "success": onSucess,
        "error": onError
    });

};
const dataTableConfig = {
    "language": {
        url: i18n_url
    },
    dom: 'Bfrt<"col-sm-5"l><"col-sm-7"p><"clearfix">',
    pageLength: 10,
    "scrollX": true,
    buttons: [
        {
            extend: 'colvis',
            text: 'Columnas a mostrar',
        },
        {
            extend: 'copy',
            text: 'Copiar',
            exportOptions: {
                columns: '.exportable'
            }
        },
        {
            extend: 'excel',
            exportOptions: {
                columns: '.exportable'
            }
        },
        {
            extend: 'pdf',
            exportOptions: {
                columns: '.exportable'
            }
        },
        {
            extend: 'print',
            text: 'Imprimir',
            exportOptions: {
                columns: '.exportable'
            }
        },
    ],
    columnDefs: [
        {
            targets: 'details-control', orderable: false,
            "defaultContent": ""
        },
        {
            targets: 'button-col', orderable: false,
            "width": "110px",
            "defaultContent": ""
        }
    ],
    "order": [[2, 'asc']]

};

$(document).ready(function () {
    ko.applyBindings(vm);
    sendAjax(homework_url, function (result) {
            $(".loader").fadeOut();
            vm.dataHeaders(result.headers);
            vm.dataEvaluations(result.evaluations);
            vm.teacherEvaluations(result.teacherEvaluations);
        let dt = $('#table').DataTable(dataTableConfig);


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
                    row.child(formatStudent(vm.dataEvaluations()[idx]), 'new-row').show();
                }
            });

    });
    sendAjax(teacher_evaluations_url, function (result) {
        $(".loader").fadeOut();
        vm.dataHeaders(result.headers);
        vm.dataEvaluationsTeacher(result.evaluations);
        let dt = $('#table2').DataTable(dataTableConfig);


        $('#table2 tbody').on('click', 'tr td.details-control', function () {
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
                row.child(formatTeacher(vm.dataEvaluationsTeacher()[idx]), 'new-row').show();
            }
        });

    });

});

