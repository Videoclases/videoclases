/*
 *  ViewModels for editing grupos to students
 */

function Alumno(id, last_name, first_name, group, videoclase) {
    var self = this;
    self.last_name = ko.observable(last_name);
    self.first_name = ko.observable(first_name);
    self.group = ko.observable(group);
    self.id = ko.observable(id);
    self.videoclase = ko.observable(videoclase);
}

function EditarGrupo() {
    var self = this;
    self.hasCurso = ko.observable(false);
    self.students = ko.observableArray();
    self.cantidadPorGrupo = ko.observable(1);
    self.alumnoActual = ko.observable();
    self.tareaActual = ko.observable();

    self.headers = [
        {title:'Apellido',sortKey:'last_name'},
        {title:'Nombre',sortKey:'first_name'},
        {title:'# Grupo',sortKey:'group'},
        {title:'Subió VideoClase',sortKey:'videoclase'}
    ];

    self.crearArrayGrupos = function() {
        var grupos = [];
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
    };

    self.asignarAleatorio = function() {
        grupos = self.crearArrayGrupos();
        for (i = 0; i < self.students().length; i++) {
            var group;
            if (parseInt(self.cantidadPorGrupo()) === 1) {
                group = grupos[i];
            } else {
                var ri = Math.floor(Math.random() * grupos.length);
                group = grupos.splice(ri, 1);
            }
            self.students()[i].group(group);
        }
    };

    self.getVideoclaseText = function(hasVideoclase) {
        if (hasVideoclase) {
            return 'Sí';
        } else {
            return 'No';
        }
    };

    self.siTodosTienenGrupo = function() {
        for (var i = 0; i < self.students().length; i++){
            var student = self.students()[i];
            if (student.group() === undefined || !student.group()) {
                return false;
            }
        }
        return true;
    };

    self.sortTable = function(sortKey) {
        switch(sortKey){
            case 'first_name':
                self.students.sort(function(a,b){
                    return a.first_name() < b.first_name() ? -1 : a.first_name() > b.first_name() ? 1 : a.first_name() === b.first_name() ? 0 : 0;
                });
                break;
            case 'last_name':
                self.students.sort(function(a,b){
                    return a.last_name() < b.last_name() ? -1 : a.last_name() > b.last_name() ? 1 : a.last_name() === b.last_name() ? 0 : 0;
                });
                break;
            case 'group':
                self.students.sort(function(a,b){
                    return a.group() < b.group() ? -1 : a.group() > b.group() ? 1 : a.group() === b.group() ? 0 : 0;
                });
                break;
            case 'videoclase':
                self.students.sort(function(a,b){
                    return a.videoclase() < b.videoclase() ? -1 : a.videoclase() > b.videoclase() ? 1 : a.videoclase() === b.videoclase() ? 0 : 0;
                });
                break;
        }
    };

    self.sort = function(header,event) {
        self.sortTable(header.sortKey);
    };

    self.submitGrupos = function(grupos, url) {
        var fd = new FormData();
        fd.append("groups", JSON.stringify(grupos));
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
            contentType: false
        });
    };

    self.validateGrupos = function() {
        var valid = true;
        var grupoNumbers = [];
        var i;
        for (i = 0; i < self.students().length; i++) {
            var group = parseInt(self.students()[i].group());
            if ($.inArray(group, grupoNumbers) === -1) {
                grupoNumbers.push(group)
            }
        }
        grupoNumbers = grupoNumbers.sort(function (a, b) { 
            return a - b;
        });
        for (i = 0; i < grupoNumbers.length; i++) {
            if (grupoNumbers[i] !== i + 1)
                valid = false;
        }
        return valid;
    }
}