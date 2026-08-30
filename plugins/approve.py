import os
import asyncio
from datetime import datetime
from config import *
from pyrogram import Client, filters
from pyrogram.types import Message, User, ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, ChatAdminRequired, RPCError, UserNotParticipant
from database.database import set_approval_off, is_approval_off, save_approved_request, get_channel_stats, get_fsub_channels
from helper_func import is_owner_or_admin, UserClient
from config import LOG_CHANNEL

# Default settings
APPROVAL_WAIT_TIME = 1  # seconds 
AUTO_APPROVE_ENABLED = False  # Toggle for enabling/disabling auto approval
user_client = None
APPROVED = "on"  # Default setting for approval messages

async def get_user_client():
    global user_client
    if user_client is None:
        user_client = UserClient("userbot", session_string=USER_SESSION, api_id=APP_ID, api_hash=API_HASH)
        await user_client.start()
    return user_client

@Client.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))  
async def autoapprove(client, message: ChatJoinRequest):  
    global AUTO_APPROVE_ENABLED  
  
    if not AUTO_APPROVE_ENABLED:  
        return  
  
    chat = message.chat  
    user = message.from_user  
  
    # check if approval is off for this channel  
    if await is_approval_off(chat.id):  
        print(f"Auto-approval is OFF for channel {chat.id}")  
        return  
  
    print(f"{user.first_name} requested to join {chat.title}")  
      
    await asyncio.sleep(APPROVAL_WAIT_TIME)  
  
    # Check if user is already a participant before approving  
    try:  
        member = await client.get_chat_member(chat.id, user.id)  
        if member.status in ["member", "administrator", "creator"]:  
            print(f"User {user.id} is already a participant of {chat.id}, skipping approval.")  
            return  
    except UserNotParticipant:
        # User is not a member, handle accordingly
        pass
    
    # Move this inside the async function
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    # ✅ TRACK APPROVED REQUEST
    await save_approved_request(
        channel_id=chat.id,
        user_id=user.id,
        username=user.username or f"{user.first_name} {user.last_name}".strip()
    )
    print(f"✅ Tracked approval - User {user.id} approved in channel {chat.id}")

    if LOG_CHANNEL:
        try:
            user_name = user.first_name or "User"
            if user.last_name:
                user_name = f"{user_name} {user.last_name}"
            
            log_text = f"""<b>✅ USER APPROVED</b>

<b>👤 Name:</b> {user_name}
<b>🆔 User ID:</b> <code>{user.id}</code>
<b>📝 Username:</b> @{user.username if user.username else "N/A"}
<b>📢 Channel:</b> {chat.title}
<b>🔗 Channel ID:</b> <code>{chat.id}</code>

━━━━━━━━━━━━━━━━━━━━━━
<b>⏰ Time:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"""
            
            await client.send_message(LOG_CHANNEL, log_text, parse_mode=ParseMode.HTML)
            print(f"✅ Logged: User {user.id} in {chat.id}")
        except Exception as e:
            print(f"Failed to log: {e}")
    
        
    if APPROVED == "on":
        invite_link = await client.export_chat_invite_link(chat.id)
        buttons = [
            [InlineKeyboardButton(f'• ʜᴇʀᴇ ɪs ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ •', url=invite_link)]
        ]
        markup = InlineKeyboardMarkup(buttons)
        caption = f"<b>Hᴇʏ {user.mention()},\n<blockquote> ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ {chat.title} ʜᴀs ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ.</blockquote> </b>"
        
        sent_msg = await client.send_photo(
            chat_id=user.id,
            photo='https://graph.org/file/2a3bdf158d2d876c474a1-8566a8ace3bc440d18.jpg',
            caption=caption,
            reply_markup=markup
        )

        await asyncio.sleep(60)
        try:
            await client.delete_messages(chat_id=user.id, message_ids=sent_msg.id)
        except Exception as e:
            print(f"Failed to delete message: {e}")

@Client.on_message(filters.command("reqtime") & is_owner_or_admin)
async def set_reqtime(client, message: Message):
    global APPROVAL_WAIT_TIME
    
    if len(message.command) != 2 or not message.command[1].isdigit():
        return await message.reply_text("Usage: <code>/reqtime {seconds}</code>")
    
    APPROVAL_WAIT_TIME = int(message.command[1])
    await message.reply_text(f"✅ Request approval time set to <b>{APPROVAL_WAIT_TIME}</b> seconds.")

@Client.on_message(filters.command("reqmode") & is_owner_or_admin)
async def toggle_reqmode(client, message: Message):
    global AUTO_APPROVE_ENABLED
    
    if len(message.command) != 2 or message.command[1].lower() not in ["on", "off"]:
        return await message.reply_text("Usage: <code>/reqmode on</code> or <code>/reqmode off</code>")
    
    mode = message.command[1].lower()
    AUTO_APPROVE_ENABLED = (mode == "on")
    status = "enabled ✅" if AUTO_APPROVE_ENABLED else "disabled ❌"
    await message.reply_text(f"Auto-approval has been {status}.")

@Client.on_message(filters.command("approveoff") & is_owner_or_admin)
async def approve_off_command(client, message: Message):
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("Usage: <code>/approveoff {channel_id}</code>")
    channel_id = int(message.command[1])
    success = await set_approval_off(channel_id, True)
    if success:
        await message.reply_text(f"✅ Auto-approval is now <b>OFF</b> for channel <code>{channel_id}</code>.")
    else:
        await message.reply_text(f"❌ Failed to set auto-approval OFF for channel <code>{channel_id}</code>.")

@Client.on_message(filters.command("approveon") & is_owner_or_admin)
async def approve_on_command(client, message: Message):
    if len(message.command) != 2 or not message.command[1].lstrip("-").isdigit():
        return await message.reply_text("Usage: <code>/approveon {channel_id}</code>")
    channel_id = int(message.command[1])
    success = await set_approval_off(channel_id, False)
    if success:
        await message.reply_text(f"✅ Auto-approval is now <b>ON</b> for channel <code>{channel_id}</code>.")
    else:
        await message.reply_text(f"❌ Failed to set auto-approval ON for channel <code>{channel_id}</code>.")

@Client.on_message(filters.command("total") & is_owner_or_admin)
async def show_channel_stats(client: Client, message: Message):
    """Show total channels and subscriptions with names"""
    temp = await message.reply("<b><i>📊 ᴡᴀɪᴛ ᴀ sᴇᴄ.. ʟᴏᴀᴅɪɴɢ ᴅᴀᴛᴀ...</i></b>", quote=True)
    
    try:
        fsub_channels = await get_fsub_channels()
        
        if not fsub_channels:
            return await temp.edit("<b>❌ No force-sub channels found.</b>")
        
        stats = await get_channel_stats()
        
        result = f"<b>📊 CHANNEL STATISTICS</b>\n\n"
        result += f"<b>Total Channels:</b> <code>{len(fsub_channels)}</code>\n"
        result += f"<b>Total Subscriptions:</b> <code>{sum(stats.values())}</code>\n\n"
        result += "<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
        result += "<b>📋 Channel Details:</b>\n\n"
        
        total_subs = 0
        for idx, channel_id in enumerate(fsub_channels, 1):
            try:
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
                channel_link = chat.invite_link or f"https://t.me/c/{str(channel_id)[4:]}"
                
                sub_count = stats.get(channel_id, 0)
                total_subs += sub_count
                
                result += f"<b>{idx}.</b> <a href='{channel_link}'>{channel_name}</a>\n"
                result += f"    <code>Channel ID:</code> <code>{channel_id}</code>\n"
                result += f"    <code>Subscriptions:</code> <code>{sub_count}</code>\n\n"
                
            except Exception as e:
                result += f"<b>{idx}.</b> <code>{channel_id}</code> — <i>⚠️ Error loading</i>\n\n"
        
        result += "<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        result += f"<b>✅ Total:</b> <code>{len(fsub_channels)} Channels | {total_subs} Subscriptions</code>"
        
        await temp.edit(
            result,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]])
        )
        
    except Exception as e:
        await temp.edit(f"<b>❌ Error loading statistics:</b>\n<code>{e}</code>")
        print(f"Error in /total command: {e}")

@Client.on_message(filters.command("reqstats") & is_owner_or_admin)
async def show_request_stats(client: Client, message: Message):
    """Show detailed approval stats for each channel"""
    temp = await message.reply("<b><i>📊 ᴡᴀɪᴛ ᴀ sᴇᴄ.. ʟᴏᴀᴅɪɴɢ ᴀᴘᴘʀᴏᴠᴀʟ ᴅᴀᴛᴀ...</i></b>", quote=True)
    
    try:
        fsub_channels = await get_fsub_channels()
        
        if not fsub_channels:
            return await temp.edit("<b>❌ No force-sub channels found.</b>")
        
        stats = await get_channel_stats()
        
        result = f"<b>📈 REQUEST APPROVAL STATISTICS</b>\n\n"
        result += f"<b>Total Channels:</b> <code>{len(fsub_channels)}</code>\n"
        result += f"<b>Total Approvals:</b> <code>{sum(stats.values())}</code>\n\n"
        result += "<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n\n"
        
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        for idx, (channel_id, count) in enumerate(sorted_stats, 1):
            try:
                chat = await client.get_chat(channel_id)
                percentage = (count / sum(stats.values()) * 100) if sum(stats.values()) > 0 else 0
                
                result += f"<b>{idx}. {chat.title}</b>\n"
                result += f"   Approvals: <code>{count}</code> ({percentage:.1f}%)\n"
                result += f"   ID: <code>{channel_id}</code>\n\n"
                
            except Exception as e:
                result += f"<b>{idx}. Channel {channel_id}</b> — ⚠️ Error\n\n"
        
        await temp.edit(
            result,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close ✖️", callback_data="close")]])
        )
        
    except Exception as e:
        await temp.edit(f"<b>❌ Error:</b> <code>{e}</code>")
        print(f"Error in /reqstats: {e}")
