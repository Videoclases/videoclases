/**
 *  ViewModel for the evaluar template, using Knockout.js
 */

function viewModel() {
    var self = this;

    self.responseValues = new ResponseValues();

    self.correctAnswer = ko.observable(false);
    self.wrongAnswer = ko.observable(false);
    self.doNotShowAnswer = ko.observable(false);
    self.correctAnswerText = ko.observable("");

    self.url = ko.observable(window.location.pathname);
    self.value = ko.computed(function() { return self.responseValues.value(); });
    self.answer = ko.observable();

    self.format = ko.observable();
    self.copyright = ko.observable();
    self.theme = ko.observable();
    self.pedagogical = ko.observable();
    self.rythm = ko.observable();
    self.originality = ko.observable();

    self.thumbUp = ko.computed(function() { 
        if (parseInt(self.value()) == 1) {
            return self.responseValues.thumbUpGreen(); 
        } else {
            return self.responseValues.thumbUpGray(); 
        }
    });
    self.thumbDown = ko.computed(function() { 
        if (parseInt(self.value()) == -1) {
            return self.responseValues.thumbDownRed(); 
        } else {
            return self.responseValues.thumbDownGray(); 
        }
    });

    self.clickSiguienteVideoclase = function() {
        if (self.answer() == undefined) {
            alert("Debes seleccionar una respuesta");
            return;
        }
        if(self.format() == undefined || self.copyright() == undefined
        || self.theme() == undefined || self.pedagogical() == undefined
        || self.pedagogical() == undefined || self.rythm() == undefined
        || self.originality() == undefined){
            alert("Debes completar la evaluación de los criterios");
            return;
        }
        self.submitEvaluacionDeAlumno();
        self.submitRespuestaDeAlumno();
    }

    self.evaluar = function(value) {
        self.responseValues.value(value);
    }

    self.submitEvaluacionDeAlumno = function(data, event) {
        var fd = new FormData();
        fd.append("value", parseInt(self.value()));

        fd.append("format", parseFloat(self.format()));
        fd.append("copyright", parseFloat(self.copyright()));
        fd.append("theme", parseFloat(self.theme()));
        fd.append("pedagogical", parseFloat(self.pedagogical()));
        fd.append("rythm", parseFloat(self.rythm()));
        fd.append("originality", parseFloat(self.originality()));

        fd.append("videoclase", parseInt(self.responseValues.videoclase()));
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax('/student/evaluar-video/' + self.responseValues.evaluacion() + '/', {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
            }
        });
    }

    self.submitRespuestaDeAlumno = function() {
        var fd = new FormData();
        fd.append("answer", self.answer());
        fd.append("videoclase", self.responseValues.videoclase());
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax('/student/evaluar-videoclase-form/', {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
                if (response.success) {
                    if (response.show_correct_answer) {
                        if (response.is_correct) {
                            self.correctAnswer(true);
                        } else {
                            self.correctAnswerText(response.correct_answer);
                            self.wrongAnswer(true);
                        }
                        setTimeout(function() { location.reload(); }, 2500);
                    } else {
                        location.reload();
                    }
                }
            }
        });
    }
}

var vm = new viewModel();