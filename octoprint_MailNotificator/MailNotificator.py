# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import octoprint.plugin
import MailSender

class MailNotification(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin):
    def on_after_startup(self):
        self._logger.info("Yow")

    def get_template_vars(self):
        return dict(url=self._settings.get(["url"]))

__plugin_name__ = "MailNotification"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Plugin can send notification about printing status"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_inplementation__ = MailNotification()