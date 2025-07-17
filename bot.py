from aiohttp import web
from plugins import web_server

import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from database.database import kingdb
from pyrogram.types import InlineKeyboardButton
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, CHANNEL_ID, PORT, OWNER_ID

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        bot_info = await self.get_me()
        self.name = bot_info.first_name
        self.username = bot_info.username
        self.uptime = datetime.now()

        self.REQFSUB = await kingdb.get_request_forcesub()
        self.CHANNEL_LIST, self.FSUB_BUTTONS = [], []
        self.REQ_FSUB_BUTTONS = {'normal': [], 'request': {}}
        await self.update_chat_ids()
                
        try:
            db_channel = await self.get_chat(CHANNEL_ID)

            if not db_channel.invite_link:
                db_channel.invite_link = await self.export_chat_invite_link(CHANNEL_ID)

            self.db_channel = db_channel
            
            test = await self.send_message(chat_id = db_channel.id, text = "Testing")
            await test.delete()

        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel and have proper Permissions, So Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info('Bot Stopped..')
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Aᴅᴠᴀɴᴄᴇ Fɪʟᴇ-Sʜᴀʀɪɴɢ ʙᴏᴛV3 Mᴀᴅᴇ Bʏ ➪ [Tᴇʟᴇɢʀᴀᴍ Usᴇʀɴᴀᴍᴇ]")
        self.LOGGER(__name__).info(f"{self.name} Bot Running..!")
        self.LOGGER(__name__).info(f"OPERATION SUCCESSFULL ✅")
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        try: await self.send_message(OWNER_ID, text = f"<b><blockquote>🤖 Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ ♻️</blockquote></b>")
        except: pass


    async def update_chat_ids(self):
        chat_ids = await kingdb.get_all_channels()
        abs_fsub = await kingdb.abstract_force_sub()
        abs_id = abs_link = None

        if abs_fsub and (abs_id:= abs_fsub[0]) and (abs_link:= abs_fsub[1]):
            chat_ids.append(abs_id)

        if not chat_ids:
            self.CHANNEL_LIST.clear()
            self.FSUB_BUTTONS.clear()
            self.REQ_FSUB_BUTTONS['normal'].clear()
            self.REQ_FSUB_BUTTONS['request'].clear()
            
            return f"<b><blockquote>❌ Nᴏ Fᴏʀᴄᴇ Sᴜʙ Cʜᴀɴɴᴇʟ Fᴏᴜɴᴅ !</b></blockquote>"

        valid_chat_ids, global_buttons, chnl_buttons, req_chnl_buttons = [], [], [], {}
        channel_infos = []

        for idx, chat_id in enumerate(chat_ids, start=1):
            try:
                url = abs_id_info = folder_link_info = ""
                
                data = await self.get_chat(chat_id)
                channel_link = data.invite_link 
                channel_name = data.title
                
                serial_name = f"Jᴏɪɴ ᴄʜᴀɴɴᴇʟ {idx}"

                if not channel_link:
                    channel_link = await self.export_chat_invite_link(chat_id)
                
                
                if abs_id == chat_id:
                    abs_id_info = "HIDE FSUB "
                    folder_link_info = f"\n• FOLDER LINK: <a href='{abs_link}'>Click here to see</a>"
                    url = abs_link
                    data.username = True
                
                temp_butn = [InlineKeyboardButton(text=serial_name, url=url or channel_link)]

                if not data.username:
                    await kingdb.add_reqChannel(chat_id)
                    req_channel_link = await kingdb.get_stored_reqLink(chat_id)

                    if not req_channel_link:
                        req_channel_link = (await self.create_chat_invite_link(chat_id=chat_id, creates_join_request=True)).invite_link
                        await kingdb.store_reqLink(chat_id, req_channel_link)

                    req_chnl_buttons[chat_id] = [InlineKeyboardButton(text=serial_name, url=req_channel_link)]

                else:
                    chnl_buttons.append(temp_butn)

                global_buttons.append(temp_butn)

                channel_infos.append(f"<b><blockquote>• {abs_id_info}ID: <code>{chat_id}</code>\n• NAME: <a href = {channel_link}>{channel_name}</a>{folder_link_info}</blockquote></b>\n")

                valid_chat_ids.append(chat_id)

            except Exception as e:
                print(f"Unable to update the {chat_id}, Reason: {e}")
                channel_infos.append(f"<blockquote expandable><b>{abs_id_info}ID: <code>{chat_id}</code>\n<i>! Eʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ᴜᴘᴅᴀᴛɪɴɢ...</i>\n\nRᴇᴀsᴏɴ:</b> {e}</blockquote>\n")
                
                continue
        
        invalid_ids = len(chat_ids) - len(valid_chat_ids)

        if invalid_ids:
            channel_infos.append(f"<blockquote expandable><b>⚠️ WARNING:</b> {invalid_ids} ᴄʜᴀɴɴᴇʟ IDs ᴍᴀʏ ᴀᴘᴘᴇᴀʀ ɪɴᴠᴀʟɪᴅ, ᴏʀ ᴛʜᴇ ʙᴏᴛ ᴍᴀʏ ɴᴏᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ᴘᴇʀᴍɪssɪᴏɴs. {invalid_ids} Cʜᴀɴɴᴇʟs cᴀɴ ɴᴏᴛ ғᴜɴᴄᴛɪᴏɴ ᴀs 'FᴏʀᴄᴇSᴜʙ' ʙᴜᴛᴛᴏɴ. Tᴏ ᴇɴᴀʙʟᴇ ᴛʜᴇ 'FᴏʀᴄᴇSᴜʙ' ғᴜɴᴄᴛɪᴏɴᴀʟɪᴛʏ ғᴏʀ {invalid_ids} ᴄʜᴀɴɴᴇʟs, ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ IDs ᴏʀ ᴇɴsᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ʜᴀs ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ᴘᴇʀᴍɪssɪᴏɴs.</blockquote>")

        self.CHANNEL_LIST = valid_chat_ids
        self.FSUB_BUTTONS = global_buttons
        self.REQ_FSUB_BUTTONS['normal'] = chnl_buttons
        self.REQ_FSUB_BUTTONS['request'] = req_chnl_buttons

        return ''.join(channel_infos)
    

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"{self.name} Bot stopped.")
