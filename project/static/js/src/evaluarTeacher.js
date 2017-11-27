/**
 *  ViewModel for the evaluar template, using Knockout.js
 */

var url_post = url_next;
function ViewModel() {
    var self = this;

    self.responseValues = new ResponseValues();
    self.loading = ko.observable(true);
    self.doNotShowAnswer = ko.observable(false);
    self.homework = ko.observable();
    self.video= ko.observable("");
    self.question= ko.observable("");
    self.msg= ko.observable("");
    self.comments = ko.observable("");
    self.videoclase_id= ko.observable();
    self.url = url_next;

    self.formErrorsVisible = ko.observable(false);

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    };

    self.url = ko.observable(window.location.pathname);
    self.answer = ko.observable();

    self.format = ko.observable();
    self.copyright = ko.observable();
    self.theme = ko.observable();
    self.pedagogical = ko.observable();
    self.rythm = ko.observable();
    self.originality = ko.observable();


    self.loadVideoInfo = function () {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax(url_api, {
            type: "get",
            processData: false,
            contentType: false,
            success: function(response){
                // debugger;
                console.log(response);
                if(response.redirect){
                    alert("Completaste todas las evaluaciones de esta tarea");
                    location.href = url_back;
                }else{
                    self.responseValues.ohterChoices(response.ohterChoices);
                    self.responseValues.correctAnswer(response.correctAnswer);
                    self.responseValues.video(response.video);
                    self.responseValues.question(response.question);
                    self.responseValues.videoclase_id(response.videoclase_id);
                    self.loading(false);
                }
            }
        });
    };

    self.clickNext = function () {
        self.url = url_next;
        self.checkValidForm();
    };
    self.clickBack = function () {
        self.url = url_back;
        self.checkValidForm();
    };

    self.checkValidForm = function () {
        if($("#answerForm").valid()){
            if(self.responseValues.criterias && self.responseValues.criterias().length > 0 ){
                for(let c of self.responseValues.criterias() ){
                    if(! c.response() === undefined){
                        alert("Debes evaluar todos los criterios!");
                        return false;
                    }
                }
            }else{
                if(self.format() === undefined || self.copyright() === undefined
                    || self.theme() === undefined || self.pedagogical() === undefined
                    || self.pedagogical() === undefined || self.rythm() === undefined
                    || self.originality() === undefined){
                    alert("Debes completar la evaluación de los criterios");
                    return false;
                }
            }

            self.msg("Guardando evaluación");
            self.loading(true);

            self.submitResponse();
            return true;
        }
        return false;
    };


    self.submitResponse = function (data, event) {
        var fd = new FormData();

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


        return $.ajax(url_post, {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
                self.loading(false);
                console.log(response);
                self.msg('Evaluación guardada, redirigiendo ...');
                location.href = self.url
            },
            error: function (response) {
                self.loading(false);
                console.log(response);
                alert('no se pudo guardar la evaluación');
            }
        });
    };

}

var vm = new ViewModel();