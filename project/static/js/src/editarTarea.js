/*
 *  ViewModel for EditarTarea template
 */

function viewModel() {
    var self = this;
    self.editarGrupo = new EditarGrupo();
    self.select = new Select();
    self.editarTareaBoolean = ko.observable(false);
    self.id = ko.observable();
    self.formErrorsVisible = ko.observable(false);
    self.formErrors = ko.observableArray();

    self.headers = [
        {title:'Apellido',sortKey:'apellido'},
        {title:'Nombre',sortKey:'name'},
        {title:'# GroupOfStudents',sortKey:'group'}
    ];

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    }

    self.course = {
        name: ko.observable(),
        id: ko.observable()
    }

    self.tareaDatosIniciales = {
        course: ko.observable(),
        description: ko.observable(),
        date_evaluation: ko.observable(),
        date_upload: ko.observable(),
        revision: ko.observable(),
        title: ko.observable(),
        video: ko.observable()
    }

    self.homework = {
        course: ko.observable(),
        description: ko.observable(),
        date_evaluation: ko.observable(),
        date_upload: ko.observable(),
        revision: ko.observable(),
        title: ko.observable(),
        video: ko.observable()
    }

    self.checkFormErrors = function() {
        var errors = false;
        self.formErrors.removeAll();
        if (!self.homework.title()) {
            errors = true;
            self.formErrors.push("Debes ingresar título a la tarea");
        }
        if (!self.homework.description()) {
            errors = true;
            self.formErrors.push("Debes ingresar descripción a la tarea");
        }
        if (!self.homework.date_upload()) {
            errors = true;
            self.formErrors.push("Debes ingresar fecha de subida");
        }
        if (!self.homework.date_evaluation()) {
            errors = true;
            self.formErrors.push("Debes ingresar fecha de evaluación");
        } else {
            if (!self.greaterThan(self.homework.date_evaluation(), self.homework.date_upload())) {
                errors = true;
                self.formErrors.push("La fecha de evaluación debe ser posterior a la fecha de subida");
            }
        }
        return errors;
    }

    self.descartarCambiosTarea = function() {
        self.editarTareaBoolean(false);
        self.homework.course(self.tareaDatosIniciales.course());
        self.homework.description(self.tareaDatosIniciales.description());
        self.homework.date_evaluation(self.tareaDatosIniciales.date_evaluation());
        self.homework.date_upload(self.tareaDatosIniciales.date_upload());
        self.homework.revision(self.tareaDatosIniciales.revision());
        self.homework.title(self.tareaDatosIniciales.title());
        self.homework.video(self.tareaDatosIniciales.video());
    }

    self.editarTarea = function() {
        self.editarTareaBoolean(true);
    }

    self.greaterThan = function(value, target) {
        var isValue = value != undefined && value != false
        var isTarget = target != undefined && target != false
        if (isValue && isTarget) {
            var reggie = /(\d{2})\/(\d{2})\/(\d{4})/;
            var valueArray = reggie.exec(value); 
            var targetArray = reggie.exec(target);
            var valueDate = new Date(
                parseInt((+valueArray[3])),
                parseInt((+valueArray[2]))-1,
                parseInt((+valueArray[1]))
            );
            var targetDate = new Date(
                parseInt((+targetArray[3])),
                parseInt((+targetArray[2]))-1,
                parseInt((+targetArray[1]))
            );
            return valueDate > targetDate;
        }
        return false;
    }

    self.submitEditarTarea = function() {
        var fd = new FormData();
        var mustSubmit = false;
        var hasErrors = self.checkFormErrors();
        if (!hasErrors) {
            if (self.homework.title().localeCompare(self.tareaDatosIniciales.title()) != 0) {
                mustSubmit = true;
                fd.append("title", self.homework.title());
            }
            if (self.homework.description().localeCompare(self.tareaDatosIniciales.description()) != 0) {
                mustSubmit = true;
                fd.append("description", self.homework.description());
            }
            if (parseInt(self.homework.course()) != parseInt(self.tareaDatosIniciales.course())) {
                mustSubmit = true;
                fd.append("course", parseInt(self.homework.course()));
            }
            if (parseInt(self.homework.revision()) != parseInt(self.tareaDatosIniciales.revision())) {
                mustSubmit = true;
                fd.append("revision", parseInt(self.homework.revision()));
            }
            if (self.homework.title().localeCompare(self.tareaDatosIniciales.title()) != 0) {
                mustSubmit = true;
                fd.append("title", self.homework.title());
            }
            if (self.homework.video()) {
                if (self.homework.video().localeCompare(self.tareaDatosIniciales.video()) != 0) {
                    mustSubmit = true;
                    fd.append("video", self.homework.video());
                }
            } else {
                if (self.tareaDatosIniciales.video()) {
                    mustSubmit = true;
                    fd.append("video", "empty video");
                }
            }
            var reggie = /(\d{2})\/(\d{2})\/(\d{4})/;
            if (self.homework.date_upload().localeCompare(self.tareaDatosIniciales.date_upload()) != 0) {
                mustSubmit = true;
                var subidaArray = reggie.exec(self.homework.date_upload());
                var subidaDate = (+subidaArray[3]) + '-' + (+subidaArray[2]) + '-'
                    +(+subidaArray[1]);
                fd.append("date_upload", subidaDate);
            }
            if (self.homework.date_evaluation().localeCompare(self.tareaDatosIniciales.date_evaluation()) != 0) {
                mustSubmit = true;
                var evaluacionArray = reggie.exec(self.homework.date_evaluation());
                var evaluacionDate = (+evaluacionArray[3]) + '-' + (+evaluacionArray[2]) + '-'
                    +(+evaluacionArray[1]);
                fd.append("date_evaluation", evaluacionDate);
            }
            if (mustSubmit) {
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
                });
                return $.ajax("/teacher/homework/" + self.id() + "/", {
                    data: fd,
                    type: "post",
                    processData: false,
                    contentType: false,
                    success: function(response){
                        $("#editar-group-form-submit").click();
                    }
                });
            } else {
                $("#editar-group-form-submit").click();
            }
        } else {
            self.changeFormErrorsVisible(true);
            $('html,body').animate({
                scrollTop: $("#top-form").offset().top},
                'slow');
        }
    }

    self.submitForms = function() {
        if (self.editarGrupo.validateGrupos()) {
            if ($("#editar-homework-form").valid()) {
                $("#editar-homework-form-submit").click();
            }
        } else {
            alert("Los números de los grupos no son consecutivos. Revisa si hay algún error.");
        }
    }

    self.submitGruposForm = function() {
        self.editarGrupo.tareaActual(self.id());
        var grupos = {};
        for (var i = 0; i < self.editarGrupo.students().length; i++) {
            student = self.editarGrupo.students()[i];
            try {
                grupos[student.group().toString()].push(student.id());
            } catch(err) {
                grupos[student.group().toString()] = [student.id()];
            }
        }
        $.when(self.editarGrupo.submitGrupos(grupos, "/teacher/editar-group-form/")).done(
            function (result) {
                if (result.success) {
                    alert("Tarea editada correctamente.");
                    window.location = '/teacher/';
                } else {
                    alert(result.message);
                }
            }
        );
    }
}

var vm = new viewModel();