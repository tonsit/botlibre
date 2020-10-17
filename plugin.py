###
# Copyright (c) 2020, oddluck <oddluck@riseup.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

from supybot.commands import *
import supybot.conf as conf
import supybot.log as log
import supybot.utils as utils
import supybot.plugins as plugins
import supybot.callbacks as callbacks
import re
import json
import requests
import sys

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("BotLibre")
except ImportError:
    _ = lambda x: x


class BotLibre(callbacks.Plugin):
    """BotLibre API Interface"""

    threaded = True
    public = True
    botNick = False

    def __init__(self, irc):
        self.__parent = super(BotLibre, self)
        self.__parent.__init__(irc)
        self.url = "https://www.botlibre.com/rest/json/chat"
        self.conversation = {}

    def getPayload(self, channel, text):
        if self.conversation[channel]:
            return {
                "application": self.registryValue("application"),
                "instance": self.registryValue("instance"),
                "message": text,
                "conversation": self.conversation[channel],
            }
        return {
            "application": self.registryValue("application"),
            "instance": self.registryValue("instance"),
            "message": text,
        }

    def filter(self, text):
        for word, filtered in self.filters().items():
            text = re.sub(word, filtered, text, flags=re.IGNORECASE)
        return text

    def filters(self):
        """These words are blocked by the botlibre api, there are probably more."""
        """The key is the blocked word, the value is the replacement."""
        return {
            "fuck" : "screw",
            "cunt" : "pussy",
            "vagina" : "pussy",
            "bitch" : "wuss",
            "whore" : "slut",
        }

    def queryBot(self, channel, nick, text):
        text = self.filter(text)
        self.conversation.setdefault(channel, None)
        self.log.info(f"BotLibre: {channel} <{nick}> {text}")
        try:
            response = self.getResponse(channel, text)
            self.log.info(f"BotLibre: reply on {channel}: {nick}: {response}")
            return response
        except:
            e = sys.exc_info()[0]
            self.log.info('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                         sys.exc_info()[1],
                                                         sys.exc_info()[2].tb_lineno))
            return None

    def getResponse(self, channel, text):
        r = requests.post(self.url, json=self.getPayload(channel, text))
        j = json.loads(r.content)
        response = j["message"]
        self.conversation[channel] = j["conversation"]
        return re.sub("<[^<]+?>", "", j["message"])

    def botlibre(self, irc, msg, args, text):
        """Manual Call to the BotLibre API"""
        channel = msg.args[0]
        if not irc.isChannel(channel):
            channel = msg.nick
        response = self.queryBot(channel, msg.nick, text)
        if response:
            irc.reply(response)

    botlibre = wrap(botlibre, ["text"])

    def doPrivmsg(self, irc, msg):
        (recipients, text) = msg.args
        for channel in recipients.split(','):
            if irc.isChannel(channel) and self.messageIsPrefixedWithBotNick(irc.nick, text):
                response = self.queryBot(channel, msg.nick, self.filterBotNickFromMessage(irc.nick, text)) 
                if response:
                    irc.reply(response)

    def filterBotNickFromMessage(self, nick, text):
        return re.sub(rf'{nick}:?\s?', '', text.strip(), flags=re.IGNORECASE)

    def messageIsPrefixedWithBotNick(self, nick, text):
        return re.match(f'^{nick}[:\s]\s?.*$', text, flags=re.IGNORECASE)

Class = BotLibre

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
