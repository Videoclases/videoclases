function ViewModel() {
    var self = this;

    self.responseValues = new ResponseValues();

    self.submitForm = function(grupo_id, alumno_id, myObservable, myVisible) {
        var fd = new FormData();
        fd.append("student", parseInt(alumno_id));
        fd.append("group", parseInt(grupo_id));
        fd.append("nota", parseFloat(myObservable()));
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax('/teacher/subir-nota/', {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
            success: function(response){
                myVisible(false);
            }
        });
    }
}

var vm = new ViewModel();