function viewModel() {
    var self = this;

    self.courses = ko.observable();

    self.select = new Select();
    self.homework = ko.observable();
    self.homeworks = ko.observableArray();
    self.onSelectChangeValue = function(value) {
        $.when($.ajax("/teacher/download-homeworks/" + value + "/")).done(
            function (result) {
                self.homeworks.removeAll();
                for (i = 0; i < result.homeworks.length; i++) {
                    var a = result.homeworks[i];
                    if(!a.has_pq ){
                        self.homeworks.push({'name':a.name, 'id':a.id});
                    }
                }
            }
        );
    };

    self.courses.subscribe(function () {
        self.onSelectChangeValue(self.courses());
    });

}
var vm = new viewModel();




$(document).ready(function() {
    ko.applyBindings(vm);
});