/**
 *  ViewModel for the evaluar template, using Knockout.js
 */

function viewModel() {
    var self = this;

    self.responseValues = new ResponseValues();

    self.url = ko.observable(window.location.pathname);
    self.valor = ko.computed(function() { return self.responseValues.valor(); });
    self.respuesta = ko.observable();
    self.thumbUp = ko.computed(function() { 
        if (parseInt(self.valor()) == 1) {
            return self.responseValues.thumbUpGreen(); 
        } else {
            return self.responseValues.thumbUpGray(); 
        }
    });
    self.thumbDown = ko.computed(function() { 
        if (parseInt(self.valor()) == -1) {
            return self.responseValues.thumbDownRed(); 
        } else {
            return self.responseValues.thumbDownGray(); 
        }
    });

    self.clickSiguienteVideoclase = function() {
        if (self.respuesta() == undefined) {
            alert("Debes seleccionar una respuesta");
            return;
        }
        $( "#respuestaForm" ).submit();
    }

    self.submitEvaluacionDeAlumno = function(data, event) {
        var inputId = event.originalEvent.explicitOriginalTarget.id;
        if (inputId.localeCompare("meGustaInput") == 0) {
            self.responseValues.valor(1);
        } else if (inputId.localeCompare("noMeGustaInput") == 0) {
            self.responseValues.valor(-1);
        } else {
            self.responseValues.valor(0);
        }
        var fd = new FormData();
        fd.append("valor", parseInt(self.valor()));
        fd.append("videoclase", parseInt(self.responseValues.videoclase()));
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax('/alumno/evaluar-video/' + self.responseValues.evaluacion() + '/', {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
            }
        });
    }
}

var vm = new viewModel();