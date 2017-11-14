$(document).ready(function() {
    ko.applyBindings(vm);
    vm.responseValues.value(0);
    vm.loadVideoInfo();
        $.validator.addClassRules('criteria', {
        required: true
    });
    $('#answerForm').validate({ // initialize the plugin
        rules: {
            answer: {
                required: true
            },
            format: {
                required: true
            },
            copyright: {
                required: true
            },
            theme: {
                required: true
            },
            pedagogical: {
                required: true
            },
            rythm: {
                required: true
            },
            originality: {
                required: true
            }
        },
        submitHandler: function (form) {
            return false;
        },
        invalidHandler: function(event, validator) {
            vm.changeFormErrorsVisible(true);
            $('html,body').animate({
                scrollTop: $("#top-form-head-line").offset().top},
                'slow');
        },
        errorPlacement: function (a,b) {
            return false;
        }
    });
});