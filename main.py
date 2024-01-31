'''
Automatically kick members who do not have more than n messages within m days.

Copyright (C) 2024  __retr0.init__

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import interactions
from interactions.api.events import MemberRemove, MessageCreate
from collections import deque
import asyncio
import datetime
from config import DEV_GUILD

'''
Autokick module
Base: autokick
'''
class ExtRetr0initAutokick(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="autokick",
        description="AutoKick System to automatically kick members"
    )

    initialised: bool = False
    started: bool = False

    ''' All members
    {
        <member id> : [message],
    }
    '''
    all_members: dict[int, deque[interactions.Message]] = {}

    ignored_roles: list[int] = []

    threshold_message: int = 10
    threshold_days: int = 30

    reference_time: datetime.datetime = datetime.datetime(1970, 1, 1)

    @module_base.subcommand("setup", sub_cmd_description="Setup the autokick feature and generate statistics")
    @interactions.check(interactions.is_owner())
    @interactions.slash_option(
        name = "th_message",
        description = "Message threshold. Default to 10.",
        required = False,
        opt_type = interactions.OptionType.INTEGER,
        min_value = 2
    )
    @interactions.slash_option(
        name = "th_days",
        description = "Threshold of calculation durations. Default to 30.",
        required = False,
        opt_type = interactions.OptionType.INTEGER,
        min_value = 1
    )
    async def command_setup(self, ctx: interactions.SlashContext, th_message: int = 10, th_days: int = 30):
        if self.kick_task.started:
            self.kick_task.stop()
        self.started = False
        self.initialised = False
        now: interactions.Timestamp = interactions.Timestamp.now()
        await ctx.defer()
        self.threshold_message = th_message
        self.threshold_days = th_days
        self.all_members = {mem.id: deque([]) for mem in ctx.guild.members if not mem.bot}
        all_channels: list = []
        for cc in ctx.guild.channels:
            if isinstance(cc, interactions.MessageableMixin):
                all_channels.append(cc)
            elif isinstance(cc, interactions.GuildForum):
                posts = await cc.fetch_posts()
                all_channels.extend(posts)
            # else:
            #     print(type(cc))
        # Get all message in the guild within the day threshold
        for channel in all_channels:
            if channel.name == "moderator-only":
                continue
            if isinstance(channel, interactions.MessageableMixin):
                async for message in channel.history(limit=0):
                    if now - message.timestamp > datetime.timedelta(days=th_days):
                        continue
                    for member in self.all_members.keys():
                        if message.author.id == member:
                            self.all_members[member].append(message)
                            break
        # Sort the message_id's according to the sent timestamp
        for member in self.all_members.keys():
            self.all_members[member] = deque(sorted(self.all_members[member], key=lambda m: m.timestamp))
        await ctx.send(f"Setup complete! The member who does not send more than {self.threshold_message} messages in {self.threshold_days} days will be kicked.")
        self.reference_time = now
        self.initialised = True

    async def kick_member(self, user: int):
        u: interactions.Member = await self.bot.fetch_member(user_id=user, guild_id=DEV_GUILD)
        if u is not None:
            # dm_channel: interactions.DMChannel = await u.fetch_dm()
            # if dm_channel is not None:
            #     dm_channel.send(f"您好。由于您在{self.threshold_days}天内在{ctx.guild.name}的发言不足{self.threshold_message}条。根据服务器规则，将把您踢出该服务器。如果您想重返本服务器的话，请重新加入。在此感谢您的理解与支持。祝一切安好。")
            u.kick(reason=f"From {self.reference_time - datetime.timedelta(days=30)} to {self.reference_time} has less than {self.threshold_message} messages")
            await asyncio.sleep(5)

    @interactions.Task.create(interactions.IntervalTrigger(hours=12))
    async def kick_task(self):
        # Start flag guard
        if not self.started:
            return
        self.reference_time = interactions.Timestamp.now()
        td: datetime.timedelta = datetime.timedelta(days=self.threshold_days)
        for member in self.all_members.keys():
            # Remove the old messages according to current reference time
            for message in list(self.all_members[member]):
                if self.reference_time - message.timestamp <= td:
                    break
                else:
                    self.all_members[member].popleft()
            member_obj: interactions.Member = await self.bot.fetch_member(member)
            if any(map(member_obj.has_role, self.ignored_roles)):
                continue
            if self.reference_time - member_obj.joined_at < datetime.timedelta(days=self.threshold_days):
                continue
            if len(self.all_members[member]) < self.threshold_message:
                await self.kick_member(member)

    @module_base.subcommand("start", sub_cmd_description="Start the AutoKick system")
    @interactions.check(interactions.is_owner())
    @interactions.slash_option(
        name = "force",
        description = "Force start without role setup",
        required = False,
        opt_type = interactions.OptionType.BOOLEAN
    )
    async def command_start(self, ctx: interactions.SlashContext, force: bool = False):
        if not self.initialised:
            await ctx.send("Please use the `setup` command at first!", ephemeral=True)
            return
        if not force and len(self.ignored_roles) == 0:
            await ctx.send("There is no ignored role configured! Please run `setup_roles` command to set it. If you want to continue, please set `force` parameter to `True`.")
            return
        kicked_members: dict[int, int] = {
            mem: len(self.all_members[mem])
            for mem  in self.all_members.keys()
            if len(self.all_members[mem]) < self.threshold_message
        }
        self.kick_task.start()
        self.started = True
        await ctx.send("AutoKick system started")

    @module_base.subcommand("stop", sub_cmd_description="Stop the Autokick task")
    @interactions.check(interactions.is_owner())
    async def command_stop(self, ctx: interactions.SlashContext):
        if self.kick_task.started:
            self.kick_task.stop()
            self.started = False
            await ctx.send("Autokick System stopped.")
        else:
            await ctx.send("Autokick System has not been started yet")

    @interactions.listen(MemberRemove)
    async def on_memberremove(self, event: MemberRemove):
        '''
        When the member is deleted from the server, remove the user from all_users dictionary
        '''
        if self.initialised:
            member_obj: interactions.Member = event.member
            if member_obj.id in self.all_members:
                self.all_members.pop(member_obj.id)

    @interactions.listen(MessageCreate)
    async def on_messagecreate(self, event: MessageCreate):
        '''
        Prepend message to the list
        '''
        if self.initialised:
            self.all_members[event.message.author.id].append(event.message)