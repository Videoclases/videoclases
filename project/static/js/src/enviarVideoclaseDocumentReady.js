
$(document).ready(function() {
    ko.applyBindings(vm);
    $('#enviar-videoclase-form').validate({ // initialize the plugin
        messages: {
            video: {
                required: "Debes ingresar el link del video"
            },
            question: {
                required: "Debes ingresar una question"
            },
            correct_alternative: {
                required: "Debes ingresar la answer correcta"
            },
            alternative_2: {
                required: "Debes ingresar answer incorrecta en Alternativa 2",
            },
            alternative_3: {
                required: "Debes ingresar answer incorrecta en Alternativa 3",
            }
        },
        rules: {
            video: {
                required: true
            },
            question: {
                required: true
            },
            correct_alternative: {
                required: true
            },
            alternative_2: {
                required: true
            },
            alternative_3: {
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