/*
 * View model for OctoPrint-Mailnotificator
 *
 * Author: Jaroslaw Dominik Krawczyk
 * License: AGPLv3
 */
$(function() {
    function MailnotificatorViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];

        self.newUrl = ko.observable();

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
        self.onBeforeBinding = function() {
            self.newUrl(self.settings.settings.plugins.helloworld.url());
            self.goToUrl();
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: MailnotificatorViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ /* "loginStateViewModel", "settingsViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_MailNotificator, #tab_plugin_MailNotificator, ...
        elements: [ /* ... */ ]
    });
});
