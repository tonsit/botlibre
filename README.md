Retrieve responses from the Bot Libre API.

## BotLibre


Previously this plugin tied into unknown commands. This made it hard to converse with the bot if the first words was also a valid command.
```
<tonsit> GamBot: do you like chatting?
\* GamBot you like honey?
<tonsit> GamBot: is there anything you'd like to say?
<GamBot> tonsit: Error: not enough values to unpack (expected 2, got 1)
```
The functionality was not ideal and detracted from the chatting experience.

Therefore, the plugin was rewritten to tie into the doPrivMsg function and responds to messages that address it by name.
Since supybot by default treats messages in this way as a command, it is necessary to disable this functionality or your bot will try to parse your messages as commands.

### Setup
Register for an account: https://www.botlibre.com/api.jsp (FREE)

```
config plugins.BotLibre.application (YOUR_APP_KEY_HERE)
config plugins.BotLibre.instance (BOT_INSTANCE_ID_HERE)
```
make the bot no longer respond to its nick as a command:
```
config supybot.reply.whenAddressedBy.nick False
```
# botlibre
