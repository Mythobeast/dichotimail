import re
from email.header import decode_header


## these two classes are duck-typed to look like MTNode without inheriting from it
class TerminateProcessing:
	def process(self, context, email):
		return True

AvailableTail = TerminateProcessing

def move_email(context, server, uid, target):
	server.copy(uid, target)
	server.store(uid, '+FLAGS', '\\Deleted')
	context.expunge = True

class MTNoOp:
	def process(self, context, email):
		return False

class MTNode:
	def __init__(self, parent):
		self.parent  = parent
		self.fail    = [MTNoOp]
		self.success = [MTNoOp]

	def process(self, context, email):
		if self.judge(context, email):
			for action in self.success:
				if action.process(context, email):
					return True
		else:
			for action in self.fail:
				if action.process(context, email):
					return True
		return False

	def judge(self, context, email):
		return True


class MTListNode(MTNode):
	def __init__(self, parent):
		super().__init__(parent)
		self.patterns = []

class Blacklist(MTListNode):
	def judge(self, context, email):
		fromaddy, encoding = decode_header(email["From"])[0]

		for pattern in self.patterns:
			if pattern.match(fromaddy):
				return True
		return False

class WhiteList(MTListNode):
	def judge(self, context, email):
		for pattern in self.patterns:
			if pattern.match(email.addr_from):
				return True
		return False

class HeadNode(WhiteList):
	pass

class MoveEmail(MTNode):
	def __init__(self, parent, target):
		super().__init__(parent)
		self.target = target

	def process(self, context, email):
		context.server.select(context.sourcefolder)
		context.server.copy(email.uid, self.target)
		context.server.store(email.uid, '+FLAGS', '\\Deleted')
		context.expunge = True

class RexMoveSpec:
	def __init__(self, rexspec, target):
		self.rexspec = rexspec
		self.pattern = re.compile(rexspec)
		self.target = target

class RegexMove(MTNode):
	def __init__(self, parent, patterns):
		super().__init__(parent)
		self.patterns = []
		for key, value in patterns.items():
			self.patterns.append(RexMoveSpec(key, value))

	def process(self, context, email):
		for pattern in self.patterns:
			if pattern.pattern.match(context.addr_from):
				# once an email is moved out of the folder,
				# it is no longer this tree's problem.
				move_email(context, context.server, context.uid, pattern.target)
				return True
		return False


