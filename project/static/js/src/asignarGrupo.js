/*
 *  ViewModels for assigning grupos to students
 */

function Alumno(id, apellido, name, group) {
    var self = this;
    self.apellido = ko.observable(apellido);
    self.name = ko.observable(name);
    self.group = ko.observable(group);
    self.id = ko.observable(id);
}

function AsignarGrupo() {
    var self = this;
    self.hasCurso = ko.observable(false);
    self.students = ko.observableArray();
    self.cantidadPorGrupo = ko.observable(1);
    self.alumnoActual = ko.observable();
    self.tareaActual = ko.observable();

    self.headers = [
        {title:'Apellido',sortKey:'apellido'},
        {title:'Nombre',sortKey:'name'},
        {title:'# GroupOfStudents',sortKey:'group'}
    ];

    self.crearArrayGrupos = function() {
        var grupos = []
        var j = 0;
        var grupoActual = 1;
        var cantidad = parseInt(self.cantidadPorGrupo());
        for (i = 0; i < self.students().length; i++) {
            if (j < cantidad) {
                grupos.push(grupoActual);
                j++;
            } else {
                grupoActual++;
                grupos.push(grupoActual);
                j = 1;
            }
        }
        return grupos;
    }

    self.asignarAleatorio = function() {
        grupos = self.crearArrayGrupos();
        for (i = 0; i < self.students().length; i++) {
            if (parseInt(self.cantidadPorGrupo()) == 1) {
                var group = grupos[i];
            } else {
                var ri = Math.floor(Math.random() * grupos.length);
                var group = grupos.splice(ri, 1);
            }
            self.students()[i].group(group);
        }
    }

    self.siTodosTienenGrupo = function() {
        for (var i = 0; i < self.students().length; i++){
            var student = self.students()[i];
            if (student.group() == undefined || !student.group()) {
                return false;
            }
        }
        return true;
    }

    self.sortTable = function(sortKey) {
        switch(sortKey){
            case 'name':
                self.students.sort(function(a,b){
                    return a.name() < b.name() ? -1 : a.name() > b.name() ? 1 : a.name() == b.name() ? 0 : 0;
                });
                break;
            case 'apellido':
                self.students.sort(function(a,b){
                    return a.apellido() < b.apellido() ? -1 : a.apellido() > b.apellido() ? 1 : a.apellido() == b.apellido() ? 0 : 0;
                });
                break;
            case 'group':
                self.students.sort(function(a,b){
                    return a.group() < b.group() ? -1 : a.group() > b.group() ? 1 : a.group() == b.group() ? 0 : 0;
                });
                break;
        }
    }

    self.sort = function(header,event) {
        self.sortTable(header.sortKey);
    };

    self.submitGrupos = function(grupos, url) {
        var fd = new FormData();
        fd.append("grupos", JSON.stringify(grupos));
        fd.append("homework", parseInt(self.tareaActual()));
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        return $.ajax(url, {
            data: fd,
            type: "post",
            processData: false,
            contentType: false,
        });
    }
}