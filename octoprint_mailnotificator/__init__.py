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
import octoprint.settings
import octoprint.filemanager
import requests
from datetime import timedelta
from PIL import Image
from io import BytesIO
import subprocess
import os
import octoprint_mailnotificator.mailsender as mailsender

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
            "shutdown": {
                "name": "Octoprint Shutdown",
                "enabled": True,
                "with_snapshot": False,
                        "message": "printer is shut down"
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
                        "message": "The printing was paused."
            },
            "printing_resumed": {
                "name": "Printing process : resumed",
                "enabled": True,
                "with_snapshot": True,
                        "message": "The printing was resumed."
            },
            "printing_cancelled": {
                "name": "Printing process : cancelled",
                "enabled": True,
                "with_snapshot": True,
                        "message": "The printing was stopped."
            },
            "printing_done": {
                "name": "Printing process : done",
                "enabled": True,
                "with_snapshot": True,
                        "message": "Printing is done! Took about {time_formatted}"
            },
            "printing_failed": {
                "name": "Printing process : failed",
                "enabled": True,
                "with_snapshot": True,
                        "message": "Printing has failed!"
            },
            "printing_progress": {
                "name": "Printing progress",
                "enabled": True,
                "with_snapshot": True,
                        "message": "📢 Printing is at {progress}%",
                        "step": 10
            }
        }				

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return {
            'password': "",
            'host_smtp': "",
            'user_email': "",
            'mail_to_send': "",
            'printer_name': "",
            'events': self.events
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
		return dict(type="settings", custom_bindings=False)

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

	def on_event(self, event, payload):
			if event == "Shutdown":
				return self.send_Mail("Shutdown")

			if event == "PrinterStateChanged":
				if payload["state_id"] == "OPERATIONAL":
					return self.send_Mail("printer_state_operational")
				elif payload["state_id"] == "ERROR":
					return self.send_Mail("printer_state_error")
				elif payload["state_id"] == "UNKNOWN":
					return self.send_Mail("printer_state_unknown")

			if event == "PrintStarted":
				return self.send_Mail("printing_started", payload)
			if event == "PrintPaused":
				return self.send_Mail("printing_paused", payload)
			if event == "PrintResumed":
				return self.send_Mail("printing_resumed", payload)
			if event == "PrintCancelled":
				return self.send_Mail("printing_cancelled", payload)

			if event == "PrintDone":
				payload['time_formatted'] = str(
					timedelta(seconds=int(payload["time"])))
				return self.send_Mail("printing_done", payload)

			return True

	def on_print_progress(self, location, path, progress):
			self.notify_event("printing_progress", {"progress": progress})

	def send_Mail(self, eventID, data={}):
			if(eventID not in self.events):
				self._logger.error(
					"Tried to notifiy on inexistant eventID : ", eventID)
				return False
			
			tmpConfig = self._settings.get(["events", eventID], merged=True)

			if tmpConfig["enabled"] != True:
				self._logger.debug(
					"Event {} is not enabled. Returning gracefully".format(eventID))
				return False
			
			 # Get snapshot if asked for
			withSnapshot =tmpConfig["with_snapshot"]
			snapshot = None
			snapshotUrl = self._settings.global_get(["webcam", "snapshot"])
			if withSnapshot and snapshotUrl is not None and "http" in snapshotUrl:
				try:
					snapshotCall = requests.get(snapshotUrl)

					# Get the settings used for streaming to know if we should transform the snapshot
					mustFlipH = self._settings.global_get_boolean(
						["webcam", "flipH"])
					mustFlipV = self._settings.global_get_boolean(
						["webcam", "flipV"])
					mustRotate = self._settings.global_get_boolean(
						["webcam", "rotate90"])

					# Only do something if we got the snapshot
					if snapshotCall:
						snapshotImage = BytesIO(snapshotCall.content)

						# Only call Pillow if we need to transpose anything
						if (mustFlipH or mustFlipV or mustRotate):
							img = Image.open(snapshotImage)

							self._logger.info("Transformations : FlipH={}, FlipV={} Rotate={}".format(
								mustFlipH, mustFlipV, mustRotate))

							if mustFlipH:
								img = img.transpose(Image.FLIP_LEFT_RIGHT)

							if mustFlipV:
								img = img.transpose(Image.FLIP_TOP_BOTTOM)

							if mustRotate:
								img = img.transpose(Image.ROTATE_90)

							newImage = BytesIO()
							img.save(newImage, 'jpg')

							snapshotImage = newImage

						snapshot = {
							'file': ("snapshot.jpg", snapshotImage.getvalue())}
						img = Image.open(snapshotImage)
						file_name = self.get_plugin_data_folder() + "/image.png"
						img.save(file_name)
				except requests.ConnectionError:
					snapshot = None
					self._logger.error(
						"{}: ConnectionError on: '{}'".format(eventID, snapshotUrl))
				except requests.ConnectTimeout:
					snapshot = None
					self._logger.error(
						"{}: ConnectTimeout on: '{}'".format(eventID, snapshotUrl))

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
					"""\r\n:sos: **mailnotificator Warning**""" + \
					"""\r\n The variable `{""" + error.args[0] + """}` is invalid for this message: """ + \
					"""\r\n Available variables: `{""" + \
					'}`, `{'.join(list(data)) + "}`"
			finally:
				user = self._settings.get("user_email")
				mail_to = self._settings.get("user_email")
				subject = "Octoprint Status"
				text = message
				server = "host_smtp"
				password = "password"
				return mailsender.send_mail(user,password,mail_to,subject,text,)
			


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Mailnotificator"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = MailnotificatorPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

