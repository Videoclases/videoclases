/*
 *  ViewModel for EditarTarea template
 */

function ViewModel() {
    var self = this;
    self.editarGrupo = new EditarGrupo();
    self.select = new Select();
    self.editarTareaBoolean = ko.observable(false);
    self.id = ko.observable();
    self.formErrorsVisible = ko.observable(false);
    self.formErrors = ko.observableArray();

    self.headers = [
        {title:'Apellido',sortKey:'last_name'},
        {title:'Nombre',sortKey:'first_name'},
        {title:'# Grupo',sortKey:'group'}
    ];

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    };

    self.course = {
        name: ko.observable(),
        id: ko.observable()
    };


    self.type_scalas = {
        name: ko.observable(),
        id: ko.observable(),
        description: ko.observable()
    };

    self.model_criteria = {
        scala: ko.observable(),
        criterias:ko.observableArray([])
    };
    self.model_criteria_initials = {
        scala: ko.observable(),
        criterias:ko.observableArray([])
    };

    self.chosen_scala = ko.observable("");
    self.model_criteria.scala.subscribe(function () {
        let val = self.model_criteria ? self.model_criteria.scala() : null;
        self.chosen_scala(val ? self.select.type_scalas.filter(d=>d.id === val)[0].description : "");

    });

    self.criterias = ko.observableArray(ko.utils.arrayMap([""], function(item) {
            return { name: ko.observable(item),description: ko.observable(item), id:ko.observable() };
        }));
    self.removeCriteria = function(child) {
            if (self.model_criteria.criterias().length <= 1) {
                vm.formErrors.removeAll();
                vm.changeFormErrorsVisible(true);
                vm.formErrors.push("Debes tener al menos un criterio");
                $('html,body').animate({
                scrollTop: $("#top-form").offset().top},
                'slow');
            }else {
             self.model_criteria.criterias.remove(child);
            }
        };
    self.addCriteria = function () {
            self.model_criteria.criterias.push({ name: ko.observable(""),description: ko.observable(""), editable: ko.observable(true) });
        };

    self.homeworkDatosIniciales = {
        course: ko.observable(),
        description: ko.observable(),
        date_evaluation: ko.observable(),
        date_upload: ko.observable(),
        revision: ko.observable(),
        title: ko.observable(),
        video: ko.observable(),
        homework_to_evaluate: ko.observable()
    };

    self.homework = {
        course: ko.observable(),
        description: ko.observable(),
        date_evaluation: ko.observable(),
        date_upload: ko.observable(),
        revision: ko.observable(),
        title: ko.observable(),
        video: ko.observable(),
        homework_to_evaluate: ko.observable()
    };

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
        if(!self.model_criteria.scala()){
               errors = true;
                self.formErrors.push("Debes seleccionar una escala de evaluación");
        }
        for(let c of self.model_criteria.criterias()){
            if(!c.name() || c.name().length < 4){
                errors = true;
                self.formErrors.push("Criterios no válidos");
                break;
            }
        }
        return errors;
    };

    self.descartarCambiosTarea = function() {
        self.editarTareaBoolean(false);
        self.homework.course(self.homeworkDatosIniciales.course());
        self.homework.description(self.homeworkDatosIniciales.description());
        self.homework.date_evaluation(self.homeworkDatosIniciales.date_evaluation());
        self.homework.date_upload(self.homeworkDatosIniciales.date_upload());
        self.homework.revision(self.homeworkDatosIniciales.revision());
        self.homework.title(self.homeworkDatosIniciales.title());
        self.homework.video(self.homeworkDatosIniciales.video());
        self.homework.homework_to_evaluate(self.homeworkDatosIniciales.homework_to_evaluate());
    };

    self.editarTarea = function() {
        self.editarTareaBoolean(true);
    };

    self.greaterThan = function(value, target) {
        var isValue = value !== undefined && value !== false;
        var isTarget = target !== undefined && target !== false;
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
    };

    self.submitEditarTarea = function() {
        var fd = new FormData();
        var mustSubmit = false;
        var hasErrors = self.checkFormErrors();
        if (!hasErrors) {
            if (self.homework.title().localeCompare(self.homeworkDatosIniciales.title()) !== 0) {
                mustSubmit = true;
            }
            fd.append("title", self.homework.title());
            if (self.homework.description().localeCompare(self.homeworkDatosIniciales.description()) !== 0) {
                mustSubmit = true;
            }
            fd.append("description", self.homework.description());
            if (parseInt(self.homework.course()) !== parseInt(self.homeworkDatosIniciales.course())) {
                mustSubmit = true;
            }
            fd.append("course", parseInt(self.homework.course()));
            if (parseInt(self.homework.revision()) !== parseInt(self.homeworkDatosIniciales.revision())) {
                mustSubmit = true;
            }
            fd.append("revision", parseInt(self.homework.revision()));
            if (self.homework.title().localeCompare(self.homeworkDatosIniciales.title()) !== 0) {
                mustSubmit = true;
            }
            fd.append("title", self.homework.title());
            if (self.homework.video()) {
                if (self.homework.video().localeCompare(self.homeworkDatosIniciales.video()) !== 0) {
                    mustSubmit = true;
                }
                fd.append("video", self.homework.video());
            } else {
                if (self.homeworkDatosIniciales.video()) {
                    mustSubmit = true;
                    fd.append("video", "empty");
                }
            }
            if(self.homework.homework_to_evaluate() !== self.homeworkDatosIniciales.homework_to_evaluate()) {
                mustSubmit = true;
                if(self.homework.homework_to_evaluate())
                    fd.append("homework_to_evaluate", self.homework.homework_to_evaluate());
                else
                    fd.append('homework_to_evaluate',self.id());
            }

            //criterias
            fd.append("scala", self.model_criteria.scala());
            if(self.model_criteria.scala !== self.model_criteria_initials.scala()){
                mustSubmit = true;
            }
            let editable_criterias = self.model_criteria.criterias().filter(d=>d.editable);
            let original_criterias = self.model_criteria_initials.criterias().filter(d=>d.editable);
            let results_criterias = [];
            for(let c of editable_criterias){
                if(c.id && c.id()){
                    let original = original_criterias.filter(d=>d.id && d.id() === c.id())[0];
                    if(c.name() !== original.name() || c.description() !== original.description()){
                        results_criterias.push({id:c.id(),name:c.name(),description:c.description(),editable:c.editable()});
                    }
                }else {
                    //new result!
                    results_criterias.push({name:c.name(),description:c.description(),editable:c.editable()})
                }
            }

            if(editable_criterias.filter(d=>d.id).length !== original_criterias.filter(d=>d.id).length){
                //must delete some criteria!
                for(let o of original_criterias.filter(d=>d.id && d.id())){
                    if(editable_criterias.filter(d=>d.id() === o.id()).length === 0){
                        //Deleted element :(
                        results_criterias.push({id:o.id(),name:o.name(),description:o.description(),editable:o.editable(),deleted:true});
                    }
                }
            }

            if(results_criterias.length > 0){
                mustSubmit = true;
                fd.append("criterias", JSON.stringify(results_criterias));
            }

            //end criterias

            var reggie = /(\d{2})\/(\d{2})\/(\d{4})/;
            var subidaArray = reggie.exec(self.homework.date_upload());
            var subidaDate = (+subidaArray[3]) + '-' + (+subidaArray[2]) + '-'
                +(+subidaArray[1]);
            fd.append("date_upload", subidaDate);
            if (self.homework.date_upload().localeCompare(self.homeworkDatosIniciales.date_upload()) !== 0) {
                mustSubmit = true;
            }

            var evaluacionArray = reggie.exec(self.homework.date_evaluation());
            var evaluacionDate = (+evaluacionArray[3]) + '-' + (+evaluacionArray[2]) + '-'
                +(+evaluacionArray[1]);
            fd.append("date_evaluation", evaluacionDate);

            if (self.homework.date_evaluation().localeCompare(self.homeworkDatosIniciales.date_evaluation()) !== 0) {
                mustSubmit = true;
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
    };

    self.submitForms = function() {
        if (self.editarGrupo.validateGrupos()) {
            if ($("#edit-homework-form").valid()) {
                $("#edit-homework-form-submit").click();
            }
        } else {
            alert("Los números de los grupos no son consecutivos. Revisa si hay algún error.");
        }
    };

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
        $.when(self.editarGrupo.submitGrupos(grupos, "/teacher/edit-group-form/")).done(
            function (result) {
                if (result.success) {
                    alert("Tarea editada correctamente.");
                    window.location = '/teacher/';
                } else {
                    alert(result.message);
                }
            }
        );
    };
}

var vm = new ViewModel();

//TODO: check later if works with jeremy user