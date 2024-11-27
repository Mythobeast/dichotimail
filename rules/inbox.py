
from mailtree.mtnode import (Blacklist, MoveEmail,
            AvailableTail, WhiteList, HeadNode)

# Inbox needs all of the email addresses that we don't want
# getting passed into the blacklist on accident
def bld_inboxhead(context):
	retval = HeadNode(None)
	list_of_lists = [context.friendslist,
	                 context.financiallist, context.vendorlist]
	retval.patterns = []
	for listfile in list_of_lists:
		with open(listfile,  'r') as infile:
			retval.patterns.extend(infile.read().splitlines())

	retval.success = [bld_friends(context, retval)]  # processing for people I know
	retval.failure = [bld_blacklist(context, retval)]
	return retval


def bld_blacklist(context, parent):
	retval = Blacklist(parent)
	with open(context.blacklist, 'r') as infile:
		retval.patterns = infile.read().splitlines()

	retval.success = [MoveEmail(retval, 'spam')]
	retval.failure = [AvailableTail()]   # processing for people I don't know
	return retval


def bld_friends(context, parent):
	# Financial is either statements or notices
	retval = WhiteList(parent)
	with open(context.friendslist, 'r') as infile:
		retval.patterns = infile.read().splitlines()

	retval.success = [MoveEmail(retval, 'friends')]
	retval.failure = [bld_financial(context, parent)]   # processing for people I don't know
	return retval


def bld_financial(context, parent):
	# Financial is either statements or notices
	retval = WhiteList(parent)
	with open(context.financiallist, 'r') as infile:
		retval.patterns = infile.read().splitlines()

	retval.success = [MoveEmail(retval, 'financial')]
	retval.failure = [AvailableTail()]   # processing for people I don't know
	return retval


def bld_vendors(context, parent):
	# Vendors are people that I get transactional emails from
	retval = WhiteList(parent)
	with open(context.vendorlist, 'r') as infile:
		retval.patterns = infile.read().splitlines()

	retval.success = [MoveEmail(retval, 'vendors')]
	retval.failure = [AvailableTail()]   # processing for people I don't know
	return retval

