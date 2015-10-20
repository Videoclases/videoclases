/*
 *  ViewModels for editing grupos to alumnos
 */

function Alumno(id, apellido, nombre, grupo, videoclase) {
    var self = this;
    self.apellido = ko.observable(apellido);
    self.nombre = ko.observable(nombre);
    self.grupo = ko.observable(grupo);
    self.id = ko.observable(id);
    self.videoclase = ko.observable(videoclase);
}

function EditarGrupo() {
    var self = this;
    self.hasCurso = ko.observable(false);
    self.alumnos = ko.observableArray();
    self.cantidadPorGrupo = ko.observable(1);
    self.alumnoActual = ko.observable();
    self.tareaActual = ko.observable();

    self.headers = [
        {title:'Apellido',sortKey:'apellido'},
        {title:'Nombre',sortKey:'nombre'},
        {title:'# Grupo',sortKey:'grupo'},
        {title:'Subió VideoClase',sortKey:'videoclase'},
    ];

    self.crearArrayGrupos = function() {
        var grupos = []
        var j = 0;
        var grupoActual = 1;
        var cantidad = parseInt(self.cantidadPorGrupo());
        for (i = 0; i < self.alumnos().length; i++) {
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
        for (i = 0; i < self.alumnos().length; i++) {
            if (parseInt(self.cantidadPorGrupo()) == 1) {
                var grupo = grupos[i];
            } else {
                var ri = Math.floor(Math.random() * grupos.length);
                var grupo = grupos.splice(ri, 1);
            }
            self.alumnos()[i].grupo(grupo);
        }
    }

    self.getVideoclaseText = function(hasVideoclase) {
        if (hasVideoclase) {
            return 'Sí';
        } else {
            return 'No';
        }
    }

    self.siTodosTienenGrupo = function() {
        for (var i = 0; i < self.alumnos().length; i++){
            var alumno = self.alumnos()[i];
            if (alumno.grupo() == undefined || !alumno.grupo()) {
                return false;
            }
        }
        return true;
    }

    self.sortTable = function(sortKey) {
        switch(sortKey){
            case 'nombre':
                self.alumnos.sort(function(a,b){
                    return a.nombre() < b.nombre() ? -1 : a.nombre() > b.nombre() ? 1 : a.nombre() == b.nombre() ? 0 : 0;
                });
                break;
            case 'apellido':
                self.alumnos.sort(function(a,b){
                    return a.apellido() < b.apellido() ? -1 : a.apellido() > b.apellido() ? 1 : a.apellido() == b.apellido() ? 0 : 0;
                });
                break;
            case 'grupo':
                self.alumnos.sort(function(a,b){
                    return a.grupo() < b.grupo() ? -1 : a.grupo() > b.grupo() ? 1 : a.grupo() == b.grupo() ? 0 : 0;
                });
                break;
            case 'videoclase':
                self.alumnos.sort(function(a,b){
                    return a.videoclase() < b.videoclase() ? -1 : a.videoclase() > b.videoclase() ? 1 : a.videoclase() == b.videoclase() ? 0 : 0;
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
        fd.append("tarea", parseInt(self.tareaActual()));
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

    self.validateGrupos = function() {
        var valid = true;
        var grupoNumbers = []
        for (var i = 0; i < self.alumnos().length; i++) {
            var grupo = parseInt(self.alumnos()[i].grupo());
            if ($.inArray(grupo, grupoNumbers) == -1) {
                grupoNumbers.push(grupo)
            }
        }
        grupoNumbers = grupoNumbers.sort(function (a, b) { 
            return a - b;
        });
        for (var i = 0; i < grupoNumbers.length; i++) {
            if (grupoNumbers[i] != i + 1)
                valid = false;
        }
        return valid;
    }
}