# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint_mailnotificator.MailSender

class MailnotificatorPlugin(octoprint.plugin.EventHandlerPlugin,
							octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.AssetPlugin,
                            octoprint.plugin.TemplatePlugin,
							octoprint.plugin.StartupPlugin,
							octoprint.plugin.ProgressPlugin):
	def __init__(self):
        # Events definition here (better for intellisense in IDE)
        # referenced in the settings too.
		self.events = {
            "startup": {
                "name": "Octoprint Startup",
                "enabled": True,
                "with_snapshot": False,
                        "message": "⏰ I just woke up! What are we gonna print today?"
            },
            "shutdown": {
                "name": "Octoprint Shutdown",
                "enabled": True,
                "with_snapshot": False,
                        "message": "💤 Going to bed now!"
            },
            "printer_state_operational": {
                "name": "Printer state : operational",
                "enabled": True,
                "with_snapshot": False,
                        "message": "✅ Your printer is operational."
            },
            "printer_state_error": {
                "name": "Printer state : error",
                "enabled": True,
                "with_snapshot": False,
                        "message": "⚠️ Your printer is in an erroneous state."
            },
            "printer_state_unknown": {
                "name": "Printer state : unknown",
                "enabled": True,
                "with_snapshot": False,
                        "message": "❔ Your printer is in an unknown state."
            },
            "printing_started": {
                "name": "Printing process : started",
                "enabled": True,
                "with_snapshot": True,
                        "message": "🖨️ I've started printing **{name}**"
            },
            "printing_paused": {
                "name": "Printing process : paused",
                "enabled": True,
                "with_snapshot": True,
                        "message": "⏸️ The printing was paused."
            },
            "printing_resumed": {
                "name": "Printing process : resumed",
                "enabled": True,
                "with_snapshot": True,
                        "message": "▶️ The printing was resumed."
            },
            "printing_cancelled": {
                "name": "Printing process : cancelled",
                "enabled": True,
                "with_snapshot": True,
                        "message": "🛑 The printing was stopped."
            },
            "printing_done": {
                "name": "Printing process : done",
                "enabled": True,
                "with_snapshot": True,
                        "message": "👍 Printing is done! Took about {time_formatted}"
            },
            "printing_failed": {
                "name": "Printing process : failed",
                "enabled": True,
                "with_snapshot": True,
                        "message": "👎 Printing has failed! :("
            },
            "printing_progress": {
                "name": "Printing progress",
                "enabled": True,
                "with_snapshot": True,
                        "message": "📢 Printing is at {progress}%",
                        "step": 10
            },
            "test": {  # Not a real message, but we will treat it as one
                "enabled": True,
                "with_snapshot": True,
                "message": "Hello hello! If you see this message, it means that the settings are correct!"
            },
        }

	def on_after_startup(self):
    		self._logger.info("Hello World! (more: %s)" % self._settings.get(["url"]))					

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return {
            'consumer_key': "",
            'host_smtp': "",
            'user_email': "",
            'mail_to_send': "",
            'username': "",
            'events': self.events,
            'allow_scripts': False,
            'script_before': '',
            'script_after': ''
        }

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/mailnotificator.js"],
			css=["css/MailNotificator.css"],
			less=["less/MailNotificator.less"]
		)
	
	def get_template_configs(self):
			return [
				dict(type="settings", custom_bindings=False)
			]
	# def get_template_vars(self):
    #     	return dict(url=self._settings.get(["url"]))
	# 		#

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			MailNotificator=dict(
				displayName="Mailnotificator Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="LordTaylor",
				repo="OctoPrint-Mailnotificator",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/LordTaylor/OctoPrint-Mailnotificator/archive/{target_version}.zip"
			)
		)

	def on_print_progress(self, storage, path, progress):
    		MailSender().send_Mail()

	def on_event(self, event, payload):
		
			if event == "Startup":
				return self.notify_event("startup")

			if event == "Shutdown":
				return self.notify_event("shutdown")

			if event == "PrinterStateChanged":
				if payload["state_id"] == "OPERATIONAL":
					return self.notify_event("printer_state_operational")
				elif payload["state_id"] == "ERROR":
					return self.notify_event("printer_state_error")
				elif payload["state_id"] == "UNKNOWN":
					return self.notify_event("printer_state_unknown")

			if event == "PrintStarted":
				return self.notify_event("printing_started", payload)
			if event == "PrintPaused":
				return self.notify_event("printing_paused", payload)
			if event == "PrintResumed":
				return self.notify_event("printing_resumed", payload)
			if event == "PrintCancelled":
				return self.notify_event("printing_cancelled", payload)

			if event == "PrintDone":
				payload['time_formatted'] = str(
					timedelta(seconds=int(payload["time"])))
				return self.notify_event("printing_done", payload)

			return True

	def on_print_progress(self, location, path, progress):
			self.notify_event("printing_progress", {"progress": progress})

	def on_settings_save(self, data):
			old_bot_settings = '{}{}{}'.format(
				self._settings.get(['url'], merged=True),
				self._settings.get(['avatar'], merged=True),
				self._settings.get(['username'], merged=True)
			)
			octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
			new_bot_settings = '{}{}{}'.format(
				self._settings.get(['url'], merged=True),
				self._settings.get(['avatar'], merged=True),
				self._settings.get(['username'], merged=True)
			)

			if(old_bot_settings != new_bot_settings):
				self._logger.info("Settings have changed. Send a test message...")
				self.notify_event("test")

	def notify_event(self, eventID, data={}):
			if(eventID not in self.events):
				self._logger.error(
					"Tried to notifiy on inexistant eventID : ", eventID)
				return False

			tmpConfig = self._settings.get(["events", eventID], merged=True)

			if tmpConfig["enabled"] != True:
				self._logger.debug(
					"Event {} is not enabled. Returning gracefully".format(eventID))
				return False

			# Special case for progress eventID : we check for progress and steps
			if eventID == 'printing_progress' and (
					int(tmpConfig["step"]) == 0
					or int(data["progress"]) == 0
					or int(data["progress"]) % int(tmpConfig["step"]) != 0
					or (int(data["progress"]) == 100)
			):
				return False

			tmpDataFromPrinter = self._printer.get_current_data()
			if tmpDataFromPrinter["progress"] is not None and tmpDataFromPrinter["progress"]["printTimeLeft"] is not None:
				data["remaining"] = int(
					tmpDataFromPrinter["progress"]["printTimeLeft"])
				data["remaining_formatted"] = str(
					timedelta(seconds=data["remaining"]))
			if tmpDataFromPrinter["progress"] is not None and tmpDataFromPrinter["progress"]["printTime"] is not None:
				data["spent"] = int(tmpDataFromPrinter["progress"]["printTime"])
				data["spent_formatted"] = str(timedelta(seconds=data["spent"]))

			self._logger.debug("Available variables for event " +
							eventID + ": " + ", ".join(list(data)))
			try:
				message = tmpConfig["message"].format(**data)
			except KeyError as error:
				message = tmpConfig["message"] + \
					"""\r\n:sos: **Octotweet Warning**""" + \
					"""\r\n The variable `{""" + error.args[0] + """}` is invalid for this message: """ + \
					"""\r\n Available variables: `{""" + \
					'}`, `{'.join(list(data)) + "}`"
			finally:
				return self.send_message(eventID, message, tmpConfig["with_snapshot"])
			


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Mailnotificator"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = MailnotificatorPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

