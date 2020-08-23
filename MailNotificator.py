# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class MailNotification(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin):
    def on_after_startup(self):
        self._logger.info("Yow")

__plugin_name__ = "MailNotification"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Plugin can send notification about printing status"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_inplementation__ = MailNotification()