/**
 *  ViewModel for the evaluar template, using Knockout.js
 */

function ViewModel() {
    var self = this;

    self.responseValues = new ResponseValues();
    self.correctAnswer = ko.observable(false);
    self.loading = ko.observable(true);
    self.wrongAnswer = ko.observable(false);
    self.doNotShowAnswer = ko.observable(false);
    self.correctAnswerText = ko.observable("");
    self.homework = ko.observable();
    self.video= ko.observable("");
    self.question= ko.observable("");
    self.msg= ko.observable("");
    self.comments = ko.observable("");
    self.videoclase_id= ko.observable();

    self.formErrorsVisible = ko.observable(false);

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    };

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
        if (parseInt(self.value()) === 1) {
            return self.responseValues.thumbUpGreen(); 
        } else {
            return self.responseValues.thumbUpGray(); 
        }
    });
    self.thumbDown = ko.computed(function() { 
        if (parseInt(self.value()) === -1) {
            return self.responseValues.thumbDownRed(); 
        } else {
            return self.responseValues.thumbDownGray(); 
        }
    });

    self.loadVideoInfo = function () {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax('/api/homework/' + self.responseValues.homework() + '/evaluate', {
            type: "get",
            processData: false,
            contentType: false,
            success: function(response){
                // debugger;
                console.log(response);
                if(response.redirect){
                    alert("Completaste todas las evaluaciones de esta tarea");
                    location.href="/";
                }else{
                    self.responseValues.alternativas(response.alternativas);
                    self.responseValues.video(response.video);
                    self.responseValues.question(response.question);
                    self.responseValues.videoclase_id(response.videoclase_id);
                    self.loading(false);
                }
            }
        });
    };

    self.clickSiguienteVideoclase = function() {

        if($("#answerForm").valid()){

            if (self.answer() === undefined) {
                alert("Debes seleccionar una respuesta");
                return;
            }

            if(self.responseValues.criterias && self.responseValues.criterias().length > 0 ){
                for(let c of self.responseValues.criterias() ){
                    if(! c.response() === undefined){
                        alert("Debes evaluar todos los criterios!");
                        return;
                    }
                }
            }else{
                if(self.format() === undefined || self.copyright() === undefined
                    || self.theme() === undefined || self.pedagogical() === undefined
                    || self.pedagogical() === undefined || self.rythm() === undefined
                    || self.originality() === undefined){
                    alert("Debes completar la evaluación de los criterios");
                    return;
                }
            }
            self.msg("Guardando evaluación");
            self.loading(true);
            self.submitEvaluacionDeAlumno();
            self.submitRespuestaDeAlumno();
        }

    };

    self.evaluar = function(value) {
        self.responseValues.value(value);
    };

    self.submitEvaluacionDeAlumno = function(data, event) {
        var fd = new FormData();
        fd.append("value", parseInt(self.value()));

        if(self.responseValues.criterias && self.responseValues.criterias()){
            let criteriasResponse = [];
            for(let c of self.responseValues.criterias()){
                criteriasResponse.push({ value: c.response(), criteria: c.id });
            }
            fd.append("criteria", JSON.stringify(criteriasResponse));
        }else {
        // deprecated
        fd.append("format", parseFloat(self.format()));
        fd.append("copyright", parseFloat(self.copyright()));
        fd.append("theme", parseFloat(self.theme()));
        fd.append("pedagogical", parseFloat(self.pedagogical()));
        fd.append("rythm", parseFloat(self.rythm()));
        fd.append("originality", parseFloat(self.originality()));
        }


        fd.append("comments", self.comments());

        fd.append("videoclase", parseInt(self.responseValues.videoclase_id()));
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax('/student/evaluar-video/', {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
            }
        });
    };

    self.submitRespuestaDeAlumno = function() {
        var fd = new FormData();
        fd.append("answer", self.answer());
        fd.append("videoclase", self.responseValues.videoclase_id());
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
                    self.loading(false);
                    if (response.show_correct_answer) {
                        if (response.is_correct) {
                            self.correctAnswer(true);
                        } else {
                            self.correctAnswerText(response.correct_answer);
                            self.wrongAnswer(true);
                        }
                        setTimeout(function() { location.href =self.url(); }, 5000);
                    } else {
                        location.href=self.url();
                    }
                }
            }
        });
    }
}

var vm = new ViewModel();