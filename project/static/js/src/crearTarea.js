/**
 *  ViewModel for the crear-homework template, using Knockout.js
 */

function ViewModel() {
    var self = this;

    self.loading = ko.observable(false);

    self.formErrorsVisible = ko.observable(false);
    self.formErrors = ko.observableArray();

    self.changeFormErrorsVisible = function (visibility) {
        self.formErrorsVisible(visibility);
    };

    self.course = {
        name: ko.observable(),
        id: ko.observable()
    };

    self.previous_scalas = {
        name: ko.observable(),
        id: ko.observable(),
        criterias: ko.observable()
    };


    self.type_scalas = {
        name: ko.observable(),
        id: ko.observable(),
        description: ko.observable()
    };


    self.select = new Select();
    self.homework = {
        description: ko.observable(""),
        course: ko.observable(),
        previous_scalas: ko.observable(),
        revision: ko.observable(3),
        title: ko.observable(""),
        video: ko.observable(""),
        date_upload: ko.observable(""),
        date_evaluation: ko.observable(""),
        homework_to_evaluate: ko.observable()
    };

    self.model_evaluation ={
        scala: ko.observable()
    };
    self.chosen_scala = ko.observable();

    self.asignarGrupo = new AsignarGrupo();

    self.indexLetter = function(index) {
        return String.fromCharCode(97 + index);
    };

    self.criterias = ko.observableArray(ko.utils.arrayMap([""], function(item) {
            return { value: ko.observable(item) };
        }));
    self.removeCriteria = function(child) {
            if (self.criterias().length <= 1) {
                vm.formErrors.removeAll();
                vm.changeFormErrorsVisible(true);
                vm.formErrors.push("Debes tener al menos un criterio");
                $('html,body').animate({
                scrollTop: $("#top-form-head-line").offset().top},
                'slow');
            }else {
             self.criterias.remove(child);
            }
        };
    self.addCriteria = function () {
            self.criterias.push({ value: ko.observable("") });
        }


    self.submitCrearTareaForm = function () {
        var fd = new FormData();
        fd.append("description", self.homework.description());
        fd.append("course", self.homework.course());
        fd.append("revision", parseInt(self.homework.revision()));
        fd.append("title", self.homework.title());
        fd.append("video", self.homework.video());
        if (self.homework.homework_to_evaluate()) fd.append("homework_to_evaluate", self.homework.homework_to_evaluate());
        var reggie = /(\d{2})\/(\d{2})\/(\d{4})/;
        var subidaArray = reggie.exec(self.homework.date_upload());
        var evaluacionArray = reggie.exec(self.homework.date_evaluation());
        var subidaDate = (+subidaArray[3]) + '-' + (+subidaArray[2]) + '-'
            + (+subidaArray[1]);
        var evaluacionDate = (+evaluacionArray[3]) + '-' + (+evaluacionArray[2]) + '-'
            + (+evaluacionArray[1]);
        fd.append("date_upload", subidaDate);
        fd.append("date_evaluation", evaluacionDate);
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax("/teacher/new-homework-form/", {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    self.asignarGrupo.tareaActual(response.id);
                    $("#asignar-group-form-submit").click();
                } else {
                    $(".loader").fadeOut("slow");
                    self.formErrors.removeAll();
                    self.changeFormErrorsVisible(true);
                    for (var i = 0; i < response.errors.length; i++) {
                        self.formErrors.push(response.errors[i]);
                    }
                    $('html,body').animate({
                            scrollTop: $("#top-form-head-line").offset().top
                        },
                        'slow');
                }
            }
        });
    };

    self.submitForms = function () {
        if ($("#crear-homework-form").valid()) {
            self.loading(true);
            $(".loader").fadeIn("slow");
            $("#crear-homework-form-submit").click();
        }
    };

    self.onSelectChangeValue = function (value) {
        $.when($.ajax("/teacher/descargar-course/" + value + "/")).done(
            function (result) {
                self.asignarGrupo.students.removeAll();
                self.course.name(result.course.name);
                self.course.id(result.course.id);
                for (i = 0; i < result.students.length; i++) {
                    var a = result.students[i];
                    self.asignarGrupo.students.push(new Alumno(parseInt(a.id), a.last_name, a.first_name));
                }
                self.asignarGrupo.hasCurso(true);
            }
        );
    };

    // Subscribe function for change in select
    self.homework.course.subscribe(function () {
        self.onSelectChangeValue(self.homework.course());
    });

    self.homework.previous_scalas.subscribe(function () {
        var val = self.homework.previous_scalas();
        if(val){
            console.log("WIII",val);
        }else{
            console.log("no value");
        }
    });

    self.submitGruposForm = function () {
        var grupos = {};
        for (var i = 0; i < self.asignarGrupo.students().length; i++) {
            student = self.asignarGrupo.students()[i];
            try {
                grupos[student.group().toString()].push(student.id());
            } catch (err) {
                grupos[student.group().toString()] = [student.id()];
            }
        }
        $.when(self.asignarGrupo.submitGrupos(grupos, "/teacher/asignar-group-form/")).done(
            function (result) {
                $(".loader").fadeOut("slow");
                alert("Tarea creada exitosamente.");
                window.location = '/teacher/';
            }
        );
    }
}

var vm = new ViewModel();