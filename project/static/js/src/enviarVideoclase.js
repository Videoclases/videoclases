function EnviarVideoclase() {
	var self = this;

    self.formErrorsVisible = ko.observable(false);
    self.formErrors = ko.observableArray();

    self.changeFormErrorsVisible = function(visibility) {
        self.formErrorsVisible(visibility);
    }
};

var vm = new EnviarVideoclase();