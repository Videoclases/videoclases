function Question() {
    var self = this;
    self.number_options = ko.observable(4);
    self.choises = ko.observableArray();

    self.setNumberOptions = function(value) {
        self.number_options = value;
    }
    
}
    