/**
 *  ViewModel for the crear-tarea template, using Knockout.js
 */

function viewModel() {
    var self = this;

    self.loading = ko.observable(false);

    self.formErrorsVisible = ko.observable(false);
    self.formErrors = ko.observableArray();

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    }

    self.curso = {
        nombre: ko.observable(),
        id: ko.observable()
    }

    self.select = new Select();
    self.tarea = {
        descripcion: ko.observable(""),
        curso: ko.observable(),
        revisiones: ko.observable(3),
        titulo: ko.observable(""),
        video: ko.observable(""),
        fecha_subida: ko.observable(""),
        fecha_evaluacion: ko.observable("")
    }

    self.asignarGrupo = new AsignarGrupo();

    self.submitCrearTareaForm = function() {
        var fd = new FormData();
        fd.append("descripcion", self.tarea.descripcion());
        fd.append("curso", self.tarea.curso());
        fd.append("revisiones", parseInt(self.tarea.revisiones()));
        fd.append("titulo", self.tarea.titulo());
        fd.append("video", self.tarea.video());
        var reggie = /(\d{2})\/(\d{2})\/(\d{4})/;
        var subidaArray = reggie.exec(self.tarea.fecha_subida());
        var evaluacionArray = reggie.exec(self.tarea.fecha_evaluacion());
        var subidaDate = (+subidaArray[3]) + '-' + (+subidaArray[2]) + '-'
            +(+subidaArray[1]);
        var evaluacionDate = (+evaluacionArray[3]) + '-' + (+evaluacionArray[2]) + '-'
            +(+evaluacionArray[1]);
        fd.append("fecha_subida", subidaDate);
        fd.append("fecha_evaluacion", evaluacionDate);
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax("/profesor/crear-tarea-form/", {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
                console.log(response);
                if (response.success) {
                    self.asignarGrupo.tareaActual(response.id);
                    $("#asignar-grupo-form-submit").click();
                } else {
                    $(".loader").fadeOut("slow");
                    self.formErrors.removeAll();
                    self.changeFormErrorsVisible(true);
                    for (var i = 0; i < response.errors.length; i++) {
                        self.formErrors.push(response.errors[i]);
                    }
                    $('html,body').animate({
                        scrollTop: $("#top-form-head-line").offset().top},
                        'slow');
                        }
            }
        });
    }

    self.submitForms = function() {
        if ($("#crear-tarea-form").valid()) {
            self.loading(true);
            $(".loader").fadeIn("slow");
            $("#crear-tarea-form-submit").click();
        }
    }

    self.onSelectChangeValue = function(value) {
        $.when($.ajax("/profesor/descargar-curso/" + value + "/")).done(
            function (result) {
                self.asignarGrupo.alumnos.removeAll();
                self.curso.nombre(result.curso.nombre);
                self.curso.id(result.curso.id);
                for (i = 0; i < result.alumnos.length; i++) {
                    var a = result.alumnos[i];
                    self.asignarGrupo.alumnos.push(new Alumno(parseInt(a.id), a.apellido, a.nombre));
                }
                self.asignarGrupo.hasCurso(true);
            }
        );
    }

    // Subscribe function for change in select
    self.tarea.curso.subscribe(function () {
        self.onSelectChangeValue(self.tarea.curso());                
    });

    self.submitGruposForm = function() {
        var grupos = {};
        for (var i = 0; i < self.asignarGrupo.alumnos().length; i++) {
            alumno = self.asignarGrupo.alumnos()[i];
            try {
                grupos[alumno.grupo().toString()].push(alumno.id());
            } catch(err) {
                grupos[alumno.grupo().toString()] = [alumno.id()];
            }
        }
        $.when(self.asignarGrupo.submitGrupos(grupos, "/profesor/asignar-grupo-form/")).done(
            function (result) {
                $(".loader").fadeOut("slow");
                alert("Tarea creada exitosamente.");
                window.location = '/profesor/';
            }
        );
    }
}

var vm = new viewModel();