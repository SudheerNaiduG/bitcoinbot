import requests
import time
import sys
import os
import asyncio
import threading
import logging
import logging.config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyrogram import Client,filters
from pyrogram.errors import FloodWait
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton)
import traceback

Bot=Client("BOT USERNAME",bot_token="ENTER YOUR BOT TOKEN",api_hash="API HASH",api_id=API ID)
print("Bot is instantiated successfully")
# set options to be headless, ..

#sys.stdout=open('test.txt','w') #to print the text to a file

options = webdriver.ChromeOptions()
options.binary_location='/app/.apt/usr/bin/google-chrome'
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

print("Chrome headless options are added")

url = "https://wazirx.com/exchange/BTC-INR"
final="Please wait.."
context=[""]*10
p=0
rise1=''
rise2=''
fall1=''
fall2=''

price_dict=dict()
up=dict()
down=dict()
thumb_url=dict()
error=0
rise_temp=dict()
fall_temp=dict()

def test():

	global final
	global context
	global p
	global rise1
	global rise2
	global fall1
	global fall2
	global thumb_url
	global error
	global rise_temp
	global fall_temp
	
	while True:
		try:
			context=[" "]*10
			p=0
			up=dict()
			down=dict()
			print("Opening webdriver")

			driver = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver',options=options)
			driver.get(url)
			print("Opened webdriver")
			time.sleep(5)

			html = driver.page_source

			soup = BeautifulSoup(html, "html.parser")
			all_divs = soup.find('div', {'class' : 'sc-iELTvK bZNgpE'})
			try:
				anchor = all_divs.find_all('a')
			except:
				continue

			for i in anchor:

				img=i.find('img')
				img_url=img.get('src')
				img_alt=img.get('alt')
				thumb_url[img_alt]=img_url



				market_name=i.find('span',{'class':'market-name-text'})

				temp=i.find('span',{'color':'#00C853','class':'sc-bwzfXH cFmqCk'})

				if temp is not None:
					market_change="+"+temp.text.encode('utf-8').decode('ascii', 'ignore')

				else:
					temp=i.find('span',{'color':'#f44336','class':'sc-bwzfXH jsJuLQ'})

					market_change="-"+temp.text.encode('utf-8').decode('ascii', 'ignore').replace("-","")

				price=i.find('span',{'class':'price-text ticker-price'}).text.encode('utf-8').decode('ascii', 'ignore')

				key=market_name.text[:-4].upper()
				price_dict[key]=key+" ("+market_change+")"+(" "*abs(15-len(key+" ("+market_change+")")))+(" "*abs(10-len(" ("+market_change+")")))+"  Price: Rs."+price
				if market_change.startswith("+"):
					up[key]=price_dict[key]
				else:																
					down[key]=price_dict[key]
				if len(context[p]+price_dict[key]+"\n")>4000:
					p+=1
					context[p]+=price_dict[key]+"\n"
				context[p]+=price_dict[key]+"\n"
				context[p]+="\n"
			final=context
			rise_temp=up
			fall_temp=down
			#sys.stdout.close()
			driver.close() # closing the webdriver
		except:
			Bot.send_message(chat_id=-1001130709310,text=traceback.format_exc())
			
print("Creating a thread to scrape wazirx.com continously")
thread1=threading.Thread(target=test)
print("Starting thread")
thread1.start()
print("Thread started and now scraping wazirx.com")

@Bot.on_inline_query()
def answer(client, inline_query):
	try:
		if inline_query:
			try:
				a=thumb_url[inline_query.query.upper()]
				inline_query.answer(
				results=[
					InlineQueryResultArticle(
			title=inline_query.query.upper(),
			input_message_content=InputTextMessageContent(
			    price_dict[inline_query.query.upper()]
			),
			description=f"Price of {inline_query.query}",
			thumb_url=thumb_url[inline_query.query.upper()],
			)
				]
			)
			except:
				inline_query.answer(
					results=[
					InlineQueryResultArticle(
						title="Bot is under maintanance.",
						input_message_content=InputTextMessageContent(
							f"{inline_query.query} is not a valid currency from wazirx"
							),
						description=f"Price of {inline_query.query}",

						)
					]
					)
	except:
		Bot.send_message(chat_id=-1001130709310,text=traceback.format_exc())

@Bot.on_message()
async def remover(client,message):

	global final
	try:
		send="Hi, with this bot you can know the price of all crypto currencies from wazirx.com.To get the list of all currencies,send\n/price all\nIf you want the price of any particular crypto currency,send\n/price currency token name \nExample : \n/price matic\n/price doge\n/price btc\n**Note: Dont use the full name of the currency.Use only the token name,like btc for bitcoin**.\nYou can also use this bot in inline mode.\nJust type this bot's username anywhere in telegram and enter the name of the currency.\nExample: @wazirxcoinpricebot matic\nYou can also add this bot to your group and use(Give the bot access to messages in group for the bot to work)"
		
		if message.text=="/start" or message.text=="/help" or message.text=="/start@wazirxcoinpricebot" or message.text=="/help@wazirxcoinpricebot":
			await message.reply_text(text=send,quote=True)

		if message.text:
			if message.text.startswith("/"):
				await Bot.send_message(chat_id=-1001130709310,text=f"message recieved from user {message.from_user.mention} : {message.text}")
				if final=="Please wait..":
					await message.reply_text(text="Try in a few seconds,still retreiving data from wazirx.com")

				elif message.text=="/rise" or message.text=="/rise@wazirxcoinpricebot":
					rise=list(rise_temp.values())
					if len("\n".join(rise))>4000:
						rise1="\n".join(rise[:(len(rise)/2)])
						rise2="\n".join(rise[(len(rise)/2):])
						await message.reply_text(text=rise1,quote=True)
						await message.reply_text(text=rise2,quote=True)
					else:
						rise="\n".join(rise)
						await message.reply_text(text=rise,quote=True)

				elif message.text=="/fall" or message.text=="/fall@wazirxcoinpricebot":
					fall=list(fall_temp.values())
					if len("\n".join(fall))>4000:
						fall1="\n".join(fall[:(len(fall)/2)])
						fall2="\n".join(fall[(len(fall)/2):])
						await message.reply_text(text=fall1,quote=True)
						await message.reply_text(text=fall2,quote=True)
					else:
						fall="\n".join(fall)
						await message.reply_text(text=fall,quote=True)



				elif len(message.text.split(" "))==2:

					split=message.text.split(" ")

					if split[0]=="/price" or split[0]=="/price@wazirxcoinpricebot":
						print("1st part of split is /price")

						if final=="Please wait":

							await message.reply_text(text=final,quote=True)

						elif split[1]=="all":

							for smth in final:
								await message.reply_text(text=smth,quote=True)

						else:
							try:
								val=price_dict[split[1].upper()]
								await message.reply_text(text=val,quote=True)

							except:
								print("key not found,send valid curreny")
								await message.reply_text(text="Please enter a valid currency name",quote=True)
	except:
		await Bot.send_message(chat_id=-1001130709310,text=traceback.format_exc())

Bot.run()
