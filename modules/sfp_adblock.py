#-------------------------------------------------------------------------------
# Name:         sfp_adblock
# Purpose:      SpiderFoot plug-in to test if external/internally linked pages
#               would be blocked by AdBlock Plus.
#
# Author:      Steve Micallef <steve@binarypool.com>
#
# Created:     22/09/2014
# Copyright:   (c) Steve Micallef 2014
# Licence:     GPL
#-------------------------------------------------------------------------------

import sys
import re
import adblockparser
from sflib import SpiderFoot, SpiderFootPlugin, SpiderFootEvent

class sfp_adblock(SpiderFootPlugin):
    """AdBlock Check: Check if linked pages would be blocked by AdBlock Plus."""

    # Default options
    opts = { 
        "blocklist": "https://easylist-downloads.adblockplus.org/easylist.txt" 
    }

    optdescs = {
        "blocklist": "AdBlockPlus block list."
    }

    results = list()
    rules = None

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc
        self.results = list()
        self.rules = None

        for opt in userOpts.keys():
            self.opts[opt] = userOpts[opt]

    # What events is this module interested in for input
    def watchedEvents(self):
        return ["LINKED_URL_INTERNAL", "LINKED_URL_EXTERNAL"]

    # What events this module produces
    # This is to support the end user in selecting modules based on events
    # produced.
    def producedEvents(self):
        return [ "URL_ADBLOCKED_INTERNAL", "URL_ADBLOCKED_EXTERNAL" ]

    # Handle events sent to this module
    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data

        self.sf.debug("Received event, " + eventName + ", from " + srcModuleName)

        if self.rules == None:
            raw = self.sf.fetchUrl(self.opts['blocklist'], timeout=30)
            if raw['content'] != None:
                lines = raw['content'].split('\n')
                self.sf.debug("RULE LINES: " + str(len(lines)))
                self.rules = adblockparser.AdblockRules(lines)
            else:
                self.sf.error("Unable to download AdBlockPlus list: " + \
                    self.opts['blocklist'])

        if "_EXTERNAL" in eventName:
            pagetype = "_EXTERNAL"
        else:
            pagetype = "_INTERNAL"

        if eventData not in self.results:
            self.results.append(eventData)
        else:
            self.sf.debug("Already checked this page for AdBlock matching, skipping.")
            return None

        if self.rules.should_block(eventData):
            evt = SpiderFootEvent("URL_ADBLOCKED" + pagetype, eventData,
                self.__name__, event.sourceEvent)
            self.notifyListeners(evt)

        return None

# End of sfp_adblock class
