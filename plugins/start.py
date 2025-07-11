# +++ Made By King [telegram username: @Shidoteshika1] +++

import os
import sys
import random
import asyncio
import subprocess
from bot import Bot
from database.database import kingdb
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from plugins.FORMATS import START_MSG, FORCE_MSG
from pyrogram.enums import ParseMode, ChatAction
from config import CUSTOM_CAPTION, OWNER_ID, PICS
from plugins.autoDelete import auto_del_notification, delete_message
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper_func import banUser, is_userJoin, is_admin, subscribed, encode, decode, get_messages


@Bot.on_message(filters.command('start') & filters.private & ~banUser & subscribed)
async def start_command(client: Client, message: Message): 
    await message.reply_chat_action(ChatAction.CHOOSE_STICKER)
    id = message.from_user.id  
    
    if not await kingdb.present_user(id):
        try: await kingdb.add_user(id)
        except: pass
                
    text = message.text        
    if len(text)>7:
        await message.delete()

        try: base64_string = text.split(" ", 1)[1]
        except: return
                
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
                    
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
                            
        elif len(argument) == 2:
            try: ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except: return
                    
        last_message = None
        await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)  
        
        try: messages = await get_messages(client, ids)
        except: return await message.reply("<b><i>Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ..!</i></b>")
            
        AUTO_DEL, DEL_TIMER, HIDE_CAPTION, CHNL_BTN, PROTECT_MODE = await asyncio.gather(kingdb.get_auto_delete(), kingdb.get_del_timer(), kingdb.get_hide_caption(), kingdb.get_channel_button(), kingdb.get_protect_content())   
        if CHNL_BTN: button_name, button_link = await kingdb.get_channel_button_link()
            
        for idx, msg in enumerate(messages):
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)

            elif HIDE_CAPTION: #and (msg.document or msg.audio):
                caption = ""

            else:
                caption = "" if not msg.caption else msg.caption.html

            if CHNL_BTN:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=button_name, url=button_link)]]) #if msg.document or msg.photo or msg.video or msg.audio else None
            else:
                reply_markup = msg.reply_markup   
                    
            try:
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.1)

                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: last_message = copied_msg

            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.1)
                
                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: last_message = copied_msg
                        
        if AUTO_DEL and last_message:
                asyncio.create_task(auto_del_notification(client.username, last_message, DEL_TIMER, message.command[1]))
                        
    else:   
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('🤖 Aʙᴏᴜᴛ ᴍᴇ', callback_data= 'about'), InlineKeyboardButton('Sᴇᴛᴛɪɴɢs ⚙️', callback_data='setting')]])

        await message.reply_photo(
            photo = random.choice(PICS),
            caption = START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup = reply_markup,
	        message_effect_id=5104841245755180586 #🔥
        )
        try: await message.delete()
        except: pass

   
##===================================================================================================================##

#TRIGGRED START MESSAGE FOR HANDLE FORCE SUB MESSAGE AND FORCE SUB CHANNEL IF A USER NOT JOINED A CHANNEL

##===================================================================================================================##   

@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def not_joined(client: Client, message: Message):
    temp = await message.reply("<i><b>Cʜᴇᴄᴋɪɴɢ...</b></i>")
    
    try:
        if not client.REQFSUB:
            buttons = client.FSUB_BUTTONS[:]
        else:
            user_id = message.from_user.id

            buttons = client.REQ_FSUB_BUTTONS['normal'][:]

            buttons.extend([
                chat_button for chat_id, chat_button in client.REQ_FSUB_BUTTONS['request'].items()
                if not await kingdb.reqSent_user_exist(chat_id, user_id)
            ])

        try:
            # Add Update (URL) button
            update_button = [InlineKeyboardButton(text='𝖬𝗈𝗋𝖾 𝖠𝗇𝗂𝗆𝖾𝗌', url='https://t.me/addlist/DjJrbINkoyIzYzE1')]
            # Add Try Again button
            try_again_button = [InlineKeyboardButton(
                text='♻️ Tʀʏ Aɢᴀɪɴ',
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )]
            # Append both buttons
            buttons.append(update_button)
            buttons.append(try_again_button)
        except IndexError:
            pass

        await temp.edit(
            text=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id,
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        try:
            await message.delete()
        except:
            pass

    except Exception as e:
        print(f"Unable to perform forcesub buttons reason : {e}")
        return await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @imakashrabha</i>\n"
            f"<blockquote expandable>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
	)

#=====================================================================================##
#......... RESTART COMMAND FOR RESTARTING BOT .......#
#=====================================================================================##

@Bot.on_message(filters.command('restart') & filters.private & filters.user(OWNER_ID))
async def restart_bot(client: Client, message: Message):
    print("Restarting bot...")
    msg = await message.reply(text=f"<b><i><blockquote>⚠️ {client.name} ɢᴏɪɴɢ ᴛᴏ Rᴇsᴛᴀʀᴛ...</blockquote></i></b>")
    try:
        await asyncio.sleep(6)  # Wait for 6 seconds before restarting
        await msg.delete()
        args = [sys.executable, "main.py"]  # Adjust this if your start file is named differently
        os.execl(sys.executable, *args)
    except Exception as e:
        print(f"Error occured while Restarting the bot: {e}")
        return await msg.edit_text(f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @imakashrabha</i></b>\n<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>")
    # Optionally, you can add cleanup tasks here
    #subprocess.Popen([sys.executable, "main.py"])  # Adjust this if your start file is named differently
    #sys.exit()
