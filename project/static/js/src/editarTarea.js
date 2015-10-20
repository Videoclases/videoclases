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
        {title:'Nombre',sortKey:'nombre'},
        {title:'# Grupo',sortKey:'grupo'}
    ];

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    }

    self.curso = {
        nombre: ko.observable(),
        id: ko.observable()
    }

    self.tareaDatosIniciales = {
        curso: ko.observable(),
        descripcion: ko.observable(),
        fecha_evaluacion: ko.observable(),
        fecha_subida: ko.observable(),
        revisiones: ko.observable(),
        titulo: ko.observable(),
        video: ko.observable()
    }

    self.tarea = {
        curso: ko.observable(),
        descripcion: ko.observable(),
        fecha_evaluacion: ko.observable(),
        fecha_subida: ko.observable(),
        revisiones: ko.observable(),
        titulo: ko.observable(),
        video: ko.observable()
    }

    self.checkFormErrors = function() {
        var errors = false;
        self.formErrors.removeAll();
        if (!self.tarea.titulo()) {
            errors = true;
            self.formErrors.push("Debes ingresar título a la tarea");
        }
        if (!self.tarea.descripcion()) {
            errors = true;
            self.formErrors.push("Debes ingresar descripción a la tarea");
        }
        if (!self.tarea.fecha_subida()) {
            errors = true;
            self.formErrors.push("Debes ingresar fecha de subida");
        }
        if (!self.tarea.fecha_evaluacion()) {
            errors = true;
            self.formErrors.push("Debes ingresar fecha de evaluación");
        } else {
            if (!self.greaterThan(self.tarea.fecha_evaluacion(), self.tarea.fecha_subida())) {
                errors = true;
                self.formErrors.push("La fecha de evaluación debe ser posterior a la fecha de subida");
            }
        }
        return errors;
    }

    self.descartarCambiosTarea = function() {
        self.editarTareaBoolean(false);
        self.tarea.curso(self.tareaDatosIniciales.curso());
        self.tarea.descripcion(self.tareaDatosIniciales.descripcion());
        self.tarea.fecha_evaluacion(self.tareaDatosIniciales.fecha_evaluacion());
        self.tarea.fecha_subida(self.tareaDatosIniciales.fecha_subida());
        self.tarea.revisiones(self.tareaDatosIniciales.revisiones());
        self.tarea.titulo(self.tareaDatosIniciales.titulo());
        self.tarea.video(self.tareaDatosIniciales.video());
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
            if (self.tarea.titulo().localeCompare(self.tareaDatosIniciales.titulo()) != 0) {
                mustSubmit = true;
                fd.append("titulo", self.tarea.titulo());
            }
            if (self.tarea.descripcion().localeCompare(self.tareaDatosIniciales.descripcion()) != 0) {
                mustSubmit = true;
                fd.append("descripcion", self.tarea.descripcion());
            }
            if (parseInt(self.tarea.curso()) != parseInt(self.tareaDatosIniciales.curso())) {
                mustSubmit = true;
                fd.append("curso", parseInt(self.tarea.curso()));
            }
            if (parseInt(self.tarea.revisiones()) != parseInt(self.tareaDatosIniciales.revisiones())) {
                mustSubmit = true;
                fd.append("revisiones", parseInt(self.tarea.revisiones()));
            }
            if (self.tarea.titulo().localeCompare(self.tareaDatosIniciales.titulo()) != 0) {
                mustSubmit = true;
                fd.append("titulo", self.tarea.titulo());
            }
            if (self.tarea.video()) {
                if (self.tarea.video().localeCompare(self.tareaDatosIniciales.video()) != 0) {
                    mustSubmit = true;
                    fd.append("video", self.tarea.video());
                }
            } else {
                if (self.tareaDatosIniciales.video()) {
                    mustSubmit = true;
                    fd.append("video", "empty video");
                }
            }
            var reggie = /(\d{2})\/(\d{2})\/(\d{4})/;
            if (self.tarea.fecha_subida().localeCompare(self.tareaDatosIniciales.fecha_subida()) != 0) {
                mustSubmit = true;
                var subidaArray = reggie.exec(self.tarea.fecha_subida());
                var subidaDate = (+subidaArray[3]) + '-' + (+subidaArray[2]) + '-'
                    +(+subidaArray[1]);
                fd.append("fecha_subida", subidaDate);
            }
            if (self.tarea.fecha_evaluacion().localeCompare(self.tareaDatosIniciales.fecha_evaluacion()) != 0) {
                mustSubmit = true;
                var evaluacionArray = reggie.exec(self.tarea.fecha_evaluacion());
                var evaluacionDate = (+evaluacionArray[3]) + '-' + (+evaluacionArray[2]) + '-'
                    +(+evaluacionArray[1]);
                fd.append("fecha_evaluacion", evaluacionDate);
            }
            if (mustSubmit) {
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
                });
                return $.ajax("/profesor/tarea/" + self.id() + "/", {
                    data: fd,
                    type: "post",
                    processData: false,
                    contentType: false,
                    success: function(response){
                        $("#editar-grupo-form-submit").click();
                    }
                });
            } else {
                $("#editar-grupo-form-submit").click();
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
            if ($("#editar-tarea-form").valid()) {
                $("#editar-tarea-form-submit").click();
            }
        } else {
            alert("Los números de los grupos no son consecutivos. Revisa si hay algún error.");
        }
    }

    self.submitGruposForm = function() {
        self.editarGrupo.tareaActual(self.id());
        var grupos = {};
        for (var i = 0; i < self.editarGrupo.alumnos().length; i++) {
            alumno = self.editarGrupo.alumnos()[i];
            try {
                grupos[alumno.grupo().toString()].push(alumno.id());
            } catch(err) {
                grupos[alumno.grupo().toString()] = [alumno.id()];
            }
        }
        $.when(self.editarGrupo.submitGrupos(grupos, "/profesor/editar-grupo-form/")).done(
            function (result) {
                if (result.success) {
                    alert("Tarea editada correctamente.");
                    window.location = '/profesor/';
                } else {
                    alert(result.message);
                }
            }
        );
    }
}

var vm = new viewModel();