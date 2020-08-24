# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import octoprint.plugin
import MailSender


class MailNotification(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin):

    def get_settings_defaults(self):
        return dict(Mail_Server="eg: smtp.gmail.com", Mail_Port="eg: 465")

    def on_after_startup(self):
        self._settings.get(["url", "AAAAAAAAAAAAAAAAA"])

    def get_template_vars(self):
        return dict(Mail_Server=self._settings.get(["smtp Mail server"],
                                                   Mail_Port=self._settings.get(["server Port"])))


__plugin_name__ = "MailNotification"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Plugin can send notification about printing status"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_inplementation__ = MailNotification()
