import email
import sys
from email.header import decode_header
from imaplib import IMAP4_SSL

from pyhocon import ConfigFactory

from dichotomail.rules.inbox import load_headfunction

imap4_client = {'host': 'imap.ionos.com', 'port': '993',
				'user': 'pr@rapplean.net', 'pass': r'naistrai'
                }

class EmailData:
	def __init__(self, num, content):
		self.num = num
		self.uid = None
		self.content = content


def main():
	context = ConfigFactory.parse_file(sys.argv[1])

	context.mc = IMAP4_SSL(imap4_client['host'], imap4_client['port'])
	context.mc.login(imap4_client['user'], imap4_client['pass'])

	for folder in context.folderlist:
		process_folder(context, folder)


	# Logout and close the connection
	context.mc.logout()


def process_folder(context, headfunction):
	headnode = load_headfunction(context, folder)
	status, rowcountlist = context.mc.select(mailbox=mailbox, readonly=False)
	if rowcountlist[0] == 0:
		return
	status, messagelist = context.mc.search(None, "ALL")
	for num in messagelist[0].split():
		status, msg_data = context.mc.fetch(num, '(RFC822)')

		for response_part in msg_data:
			if isinstance(response_part, tuple):
				# Parse a bytes email into a message object
				msg = email.message_from_bytes(response_part[1])

				# Decode email subject
				subject, encoding = decode_header(msg["Subject"])[0]
				headnode.process(context, msg)

				if isinstance(subject, bytes):
					# If subject is bytes, decode to string
					subject = subject.decode(encoding if encoding else "utf-8")
				print("Subject:", subject)
				# If the email message is multipart
				if msg.is_multipart():
					# Iterate over each part
					for part in msg.walk():
						# Extract content type of email
						content_type = part.get_content_type()
						content_disposition = str(part.get("Content-Disposition"))

						try:
							# Get the email body
							body = part.get_payload(decode=True).decode()
							print("Body:", body)
						except:
							pass
				else:
					# If the email is not multipart
					body = msg.get_payload(decode=True).decode()
					print("Body:", body)
	if context.expunge:
		context.mc.expunge()


if __name__ == '__main__':
	sys.argv.append('/Users/robertrapplean/etc/thaum/mailtree.cfg')
	main()
