from typing import Type, List

from mautrix.types import EventType, UserID
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper

from maubot import Plugin, MessageEvent
from maubot.handlers import event, command


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("rooms")


class BouncyBot(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()
        self.log.debug("Loaded %s from config example 2", self.config["example_2.value"])

    async def stop(self) -> None:
        await super().stop()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new("bouncybot")
    @command.argument("user_id", "user ID", required=False)
    async def bouncybot(self, evt: MessageEvent, user_id: UserID) -> None:
        if not user_id:
            user_id = evt.sender
        room_list: List[UserID] = self.config["rooms"].setdefault(evt.room_id, [])
        if user_id in room_list:
            room_list.remove(user_id)
            if len(room_list) == 0:
                del self.config["rooms"][evt.room_id]
            await evt.reply(f"Disabled bouncing for [{user_id}](https://matrix.to/#/{user_id})")
        else:
            room_list.append(user_id)
            await evt.reply(f"Enabled bouncing for [{user_id}](https://matrix.to/#/{user_id})")
        self.config.save()

    @event.on(EventType.ROOM_MESSAGE)
    async def handle_message(self, evt: MessageEvent) -> None:
        try:
            if evt.sender not in self.config["rooms"][evt.room_id]:
                return
        except KeyError:
            return
        await self.client.send_message_event(evt.room_id, "xyz.maubot.bounce", {})
