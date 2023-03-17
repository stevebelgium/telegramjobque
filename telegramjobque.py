# Import the necessary modules from the telegram package
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Define a function that sends a message when a website content has changed
def send_message_when_website_content_has_changed(context: CallbackContext):
	
	# Use the global variable
	global previous_content

	# Send a GET request to the website
	try:
		response = requests.get(webpage_url)

		# Check if the response status code is 200 (success)
		if response.status_code == 200:
			current_content = response.text
			
			# Check if the content has changed since the last poll
			if previous_content != current_content:
				
				# If the content has changed, send a message to notify the users
				if previous_content != "":
					context.bot.send_message(chat_id=context.job.context, text=f'The website content \n{webpage_url} \n has changed!')
				
				# Update the chat_data with the new content
				previous_content = current_content

	except:
		# If there is an error retrieving the website, send an error message
		context.bot.send_message(chat_id=context.job.context, text= f'Error retrieving {webpage_url}')

# Define a function that checks if a URL is valid
def is_url_valid(url_to_check):
	try:
		# Send a GET request to the URL and return True if the response status code is 200
		return requests.get(url_to_check).status_code == 200
	except:
		# If there is an error retrieving the URL, return False
		return False

# Define a function that starts the polling job
def start_check_command(update: Update, context: CallbackContext) -> None:
	"""Handler function for the /start_check command"""

	# Use the global variables
	global previous_content
	global webpage_url

	polling_interval = 10

	# Get the polling job from the chat_data
	job = context.chat_data.get('polling_job')
	
	if job:
		# If a polling job is already running, send a message to notify the users
		update.message.reply_text('A polling job is already running!')
	else:
		# Set the previous_content to an empty string and set the webpage_url to the input argument if it is a valid URL
		previous_content = ""
		webpage_url = context.args[0] if len(context.args) > 0 and is_url_valid(context.args[0]) else "https://medium.com/feed/@steve.dua"
		
		# Start the repeating job to check the website content every 10 seconds
		job = context.job_queue.run_repeating(send_message_when_website_content_has_changed, interval=polling_interval, first=0, context=update.message.chat_id)
		
		# Store the job in the chat_data for later reference
		context.chat_data['polling_job'] = job
		
		# Send a message to confirm the polling job has started
		update.message.reply_text(f'Polling job every {polling_interval} seconds for the site \n{webpage_url} \nhas started!')
		
def stop_check_command(update: Update, context: CallbackContext) -> None:
    """Handler function for the /stop_check command"""
    
    job = context.chat_data.get('polling_job')
    
    # Cancel the job if it exists
    if job:
        job.schedule_removal()  # remove the repeating job from the job queue
        del context.chat_data['polling_job']  # remove the job from the context
        update.message.reply_text('Polling job has stopped!')  # send a message to confirm the polling job has stopped
    else:
        update.message.reply_text('There is no active polling job!')  # send a message indicating that there is no active job


def main():
    """Main function to start the bot and handle commands"""
    
    # Create the Updater and pass it your bot's token.
    updater = Updater("<<your_telegram_api_key>>")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers for /start_check and /stop_check
    dispatcher.add_handler(CommandHandler("start_check", start_check_command))
    dispatcher.add_handler(CommandHandler("stop_check", stop_check_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
	main()