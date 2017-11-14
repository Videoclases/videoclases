
function ViewModel() {
    let self = this;
    self.loading = ko.observable(true);
    self.dataEvaluations = ko.observableArray([]);
    self.dataHeaders = ko.observableArray([]);
    self.teacherEvaluations = ko.observable();
}

let vm = new ViewModel();

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
            $('#table').dataTable( {
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
                ]
            } );

        }
    } );

});