
$(document).ready(function() {
    ko.applyBindings(vm);
    $('#enviar-videoclase-form').validate({ // initialize the plugin
        messages: {
            video: {
                required: "Debes ingresar el link del video"
            },
            pregunta: {
                required: "Debes ingresar una pregunta"
            },
            alternativa_correcta: {
                required: "Debes ingresar la respuesta correcta"
            },
            alternativa_2: {
                required: "Debes ingresar respuesta incorrecta en Alternativa 2",
            },
            alternativa_3: {
                required: "Debes ingresar respuesta incorrecta en Alternativa 3",
            }
        },
        rules: {
            video: {
                required: true
            },
            pregunta: {
                required: true
            },
            alternativa_correcta: {
                required: true
            },
            alternativa_2: {
                required: true
            },
            alternativa_3: {
                required: true
            }
        },
        invalidHandler: function(event, validator) {
            vm.formErrors.removeAll();
            vm.changeFormErrorsVisible(true);
            for (var i = 0; i < validator.errorList.length; i++){
                vm.formErrors.push(validator.errorList[i].message);
            }
            $('html,body').animate({
                scrollTop: $("#top-form-head-line").offset().top},
                'slow');
        },
        errorPlacement: function(){
            return false;  // suppresses error message text
        }
    });
});