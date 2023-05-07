import openai
import config
from telethon.sync import TelegramClient, events
import time

openai.api_key = config.API_KEY
api_id = config.API_ID
api_hash = config.API_HASH

ai_name = "Аврора"
human_name = "неизвестный"
ai_mode = f"Притворись что ты секретарша по имени {ai_name} и работаешь на человека по имени Акмаль. Далле идет разговор с {ai_name} и с неизвестными людьми которые хотят связаться с Акмалем. Никто не должен беспокоить Акмаля, а ты временно отвечаешь вместо него. Для начала представься."

chat_history = {}

client = TelegramClient('Avrora_ai', api_id, api_hash)
flag = True

def gpt(text):
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = text,
        temperature = 0.5,
        max_tokens = 300,
        top_p = 0.3,
        frequency_penalty = 0.5,
        presence_penalty = 0.0,
        stop = [f"{ai_name}: ", f"{human_name}: "]
    )
    return response

def get_response(userprompt, user_id):
    global chat_history, openai
    if user_id not in chat_history or len(chat_history[user_id]) > (4097 - 400): # max 4116
        chat_history[user_id] = ai_mode

    userprompt = f"{chat_history[user_id]}\n{human_name}: {userprompt}\n{ai_name}: "
    try:
        response = gpt(userprompt)
    except Exception as e:
        print(e)
        print("clearing chat history and reimporting openai")
        try:
            del openai
            import openai
            openai.api_key = config.API_KEY
            response = gpt(userprompt)
        except Exception as e:
            print(e)
            return False

    chat_history[user_id] = f"{userprompt}{response.choices[0].text.strip()}"
    return response.choices[0].text.strip()



@client.on(events.NewMessage(outgoing=True, pattern='.on'))
async def on(event):
    global flag
    flag = True
    await event.edit(f"{ai_name} is turned on!")


@client.on(events.NewMessage(outgoing=True, pattern='.off'))
async def on(event):
    global flag
    flag = False
    await event.edit(f"{ai_name} is turned off!")

@client.on(events.NewMessage(incoming=True))
async def get_message(event):
    if flag and event.is_private and event.message.media == None: # or event.message.mentioned:  # only auto-reply to private chats
        from_ = await event.get_sender()
        if not from_.bot:
            response = get_response(event.message.message, event.chat_id)
            if not response: return
            orig_text = "<b>Автоответчик:</b>\n<code>" + response + "</code>"
            ms_edit = await event.reply(orig_text, parse_mode='html')

            text = orig_text.split()
            text = text[1:]
            tbp = "" # to be printed
            typing_symbol = "░"
            try:
                for word in text:
                    await client.edit_message(ms_edit, tbp + typing_symbol, parse_mode='html')
                    tbp += word + " "
                    time.sleep(0.05)
                    await client.edit_message(ms_edit, tbp, parse_mode='html')
                    time.sleep(0.05)
            except Exception as e:
                print(e)
            await client.edit_message(ms_edit, orig_text, parse_mode='html')
            print('\n', "lats chat history: ------------------")
            for i in chat_history:
                print("---------", i, "---------")
                print(chat_history[i], '\n')


def main():
    try:
        client.start()
        # client.send_message(client.get_me(), f'<b>assistant {ai_name} has been started.\nEnter <code>.on</code> or <code>.off</code></b>', parse_mode='html')
        print(f'{ai_name} has been started')
        client.run_until_disconnected()
    finally:
        client.disconnect()
        print(f'{ai_name} has been stopped')


if __name__ == "__main__":
    main()