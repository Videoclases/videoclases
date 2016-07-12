/**
 *  ViewModel for the crear-homework template, using Knockout.js
 */

function viewModel() {
    var self = this;

    self.loading = ko.observable(false);

    self.formErrorsVisible = ko.observable(false);
    self.formErrors = ko.observableArray();

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    };

    self.courses = ko.observable();

    self.select = new Select();
    self.homework = ko.observable();
    self.days = ko.observable(0);
    self.hours = ko.observable(0);
    self.min = ko.observable(0);
    self.homeworks = ko.observableArray();
    self.title = ko.observable();
    self.onSelectChangeValue = function(value) {
        $.when($.ajax("/teacher/download-homeworks/" + value + "/")).done(
            function (result) {
                self.homeworks.removeAll();
                for (i = 0; i < result.homeworks.length; i++) {
                    var a = result.homeworks[i];
                    if(!a.has_pq){
                        self.homeworks.push({'name':a.name, 'id':a.id});
                    }
                }
            }
        );
    };

    self.courses.subscribe(function () {
        self.onSelectChangeValue(self.courses());
    });
    self.indexLetter = function(index) {
    return String.fromCharCode(97 + index);
  }

    self.description = ko.observable();

    var Question = function() {
        var self = this;
        self.title = ko.observable("");
        self.choices = ko.observableArray(ko.utils.arrayMap(["", "","","no se"], function(item) {
            return { value: ko.observable(item) };
        }));
        self.removeChoice = function(child) {
            if (self.choices().length <= 2) {
                vm.formErrors.removeAll();
                vm.changeFormErrorsVisible(true);
                vm.formErrors.push("Debes tener al menos dos opciones en cada pregunta");
                $('html,body').animate({
                scrollTop: $("#top-form-head-line").offset().top},
                'slow');
            }else {
             self.choices.remove(child);
            }

        };
        self.addChoice = function () {
            self.choices.push({ value: ko.observable("") });
        }
    };

    self.questions = ko.observableArray([
           new Question()
        ]);

    self.addQuestion = function () {
        this.questions.push(new Question());
    };


    self.submitCrearTareaForm = function() {
        var fd = new FormData();
        fd.append("description", self.description() || '');
        var total_min = parseInt(self.days()*24*60) + parseInt(self.hours()*60)+ self.min();
        var hours = parseInt(total_min/60);
        var min = total_min - hours*60;
        fd.append("delta_time", hours+":"+min+":00");
        fd.append("homework", self.homework());
        fd.append("title", self.title());
        fd.append("questions", ko.toJSON(self.questions()));
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax("/teacher/new-test-conceptual-form/", {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
                if (!response.success) {
                    $(".loader").fadeOut("slow");
                    self.formErrors.push("Formulario no válido");
                    $('html,body').animate({
                        scrollTop: $("#top-form-head-line").offset().top},
                        'slow');
                        }
            }
        });
    }

    self.check_time = function (add_animation) {
        if((self.days() + self.hours()+ self.min()) > 0)  {
            return true;
        }else{
            vm.formErrors.push("La duración total del test debe ser mayor a 0");
            if(add_animation){
                vm.changeFormErrorsVisible(true);
                $('html,body').animate({
                    scrollTop: $("#top-form-head-line").offset().top},
                    'slow');
            }
            return false;
        }
    }

    self.submitForms = function() {
        $(".alternative").each(function(i, $input) {$($input).rules( "add", {
          required: true,
          minlength: 2,
          messages: {
                required: "Debes escribir en todas las alternativas",
                minlength:"Las alternativas deben tener al menos 2 carácteres"
          }
        });});
        if ($("#crear-homework-form").valid() && self.check_time(true)) {
            self.loading(true);
            $(".loader").fadeIn("slow");
            self.submitCrearTareaForm();
        }
    }

}
var vm = new viewModel();


$(document).ready(function() {
    ko.applyBindings(vm);
    $(".loader").fadeOut();
    $('#crear-homework-form').validate({ // initialize the plugin
        messages: {
            course: {
                required: "Debes seleccionar un curso"
            }, 
            homework: {
                required: "Debes seleccionar una tarea"
            },
            days: {
                required: "Debes seleccionar un dia válido",
                min: "Debes seleccionar dias mayor que 0"
            },
            hours: {
                required: "Debes seleccionar una hora válida",
                min: "Debes seleccionar horas mayor que 0"
            },
            min: {
                required: "Debes seleccionar unos minutos válidos",
                min: "Debes seleccionar minutos mayor que 0"
            },
            question:{
                required: "Debes escribir todas las preguntas",
                minlength:"Las preguntas deben tener al menos 2 carácteres"
            },
            alternative:{
                required: "Debes escribir en todas las alternativas",
                minlength:"Las alternativas deben tener al menos 2 carácteres"
            },
            title:{
                maxlength:"Título demasiado largo"
            }
        },
        rules: {
            course: {
                required: true
            },
            homework: {
                required: true
            },
            days: {
                required: true,
                number:true,
                min:0
            },
            hours: {
                required: true,
                number:true,
                min:0
            },
            min: {
                required: true,
                number:true,
                min:0
            },
            question:{
                required: true,
                minlength:2
            },
            alternative:{
                required: true,
                minlength:2
            },
            title:{
                required: true,
                maxlength: 255
            }
        },
        submitHandler: function (form) {
            return false;
        },
        invalidHandler: function(event, validator) {
            vm.formErrors.removeAll();
            vm.changeFormErrorsVisible(true);
            for (var i = 0; i < validator.errorList.length; i++){
                vm.formErrors.push(validator.errorList[i].message);
            }
            vm.check_time(false);
            $('html,body').animate({
                scrollTop: $("#top-form-head-line").offset().top},
                'slow');
        },
        errorPlacement: function (a,b) {
            return false;
        }
    });
});