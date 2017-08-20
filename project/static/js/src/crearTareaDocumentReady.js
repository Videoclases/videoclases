
$(document).ready(function() {
    ko.applyBindings(vm);
    $(".loader").fadeOut();
    $.validator.addMethod(
        "greaterThan",
        function(value, element, params) {
            var target = $(params).val();
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
        },
        'Debe ser posterior a fecha de subida.');
    $('#crear-homework-form').validate({ // initialize the plugin
        messages: {
            title: {
                required: "Debes ingresar título a la tarea"
            },
            description: {
                required: "Debes ingresar descripción a la tarea"
            },
            date_upload: {
                required: "Debes ingresar fecha de subida"
            },
            date_evaluation: {
                required: "Debes ingresar fecha de evaluación",
                greaterThan: "La fecha de evaluación debe ser posterior a la fecha de subida"
            }
        },
        rules: {
            title: {
                required: true
            },
            description: {
                required: true
            },
            course: {
                required: true
            },
            revision: {
                required: true
            },
            date_upload: {
                required: true
            },
            date_evaluation: {
                required: true,
                greaterThan: '#id_fecha_subida'
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
            if (!vm.asignarGrupo.siTodosTienenGrupo()) {
                vm.formErrors.push("Debes asignar grupo a todos los estudiantes");
            }
            $('html,body').animate({
                scrollTop: $("#top-form-head-line").offset().top},
                'slow');
        },
        errorPlacement: function (a,b) {
            return false;
        }
    });
});