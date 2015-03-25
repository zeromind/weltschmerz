#!/usr/bin/python3

import random
import logging

class udpthread(threading.Thread):
	'''Thread that runs a UDP request queue. Handles timeouts, errors,
	MTU, and flood control automatically. Not bad for datagrams, huh?'''

	def __init__(self, local_port, remote_port, remote_host):
		threading.Thread.__init__(self)
		self.queue_query = Queue.Queue(5)
		self.queue_result = Queue.Queue(5)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self.sock.bind(('0.0.0.0', local_port))
		except Exception:
			self.sock.bind(('0.0.0.0', random.randint(10000,20000)))
		self.sock.settimeout(20)

	def run(self):
		last_cmd_sent = time.time()
		while True:
			if not self.queue_query.empty():
				# This thread's in is the system's out.
				outbound = self.queue_query.get(False)
				print("UDP: Sending", outbound)
				self.sock.sendto(outbound, (server, port))
				try:
					inbound = self.sock.recv(1400)
					print("UDP: Received", inbound)
					if inbound[0:3]  ==  "505":
						print("Error: Server returned 'Illegal input recieved.'\nThe program's state may not be consistent. Please restart\nthe program, and email the following to the developers:\n\nUDP: Sent " + outbound + "\nUDP: Recieved " + inbound)
					elif inbound[0:3]  ==  "555":
						print("Error: You have been temporarily banned. Common reasons include:\n - You have flooded the server with too many requests\n - You have logged in too many times from this IP without logging out\nBans may last anywhere from 5 minutes to 30 minutes. Please be patient\n and try again later. Thanks!")
					self.o.put(inbound.decode("utf8"))
					last_cmd_sent = time.time()
				except socket.timeout:
					print("UDP: Timeout!")
					print("Error: Database timed out. You may be flooding,\nor the server may be down for maintenance.\nPlease wait a second and then try again.")
					self.o.put(None)
			if time.time() >= last_cmd_sent+300:
				#we haven't sent anything to the server in the past 5min. let's send a ping to keep connectivity
				self.queue_query.put("PING nat=1")
				last_cmd_sent = time.time()
			time.sleep(5)
			
			
	def codeparser(self, tmp):
		try:
			(code, data) = tmp.split(" ", 1)
			reply_code = int(code)
			#print data
			#sed -e 's/\(.*\w\)\s*=\s\([0-9][0-9][0-9]\)/\t\t\tif reply_code == \2:\n\t\t\t\t"""\1"""\n\t\t\t\treturn False/' errorcodes > parsed_codes
			"""all return codes are set to False to fail by default. enable them as you need to"""
			if reply_code == 200:
				"""LOGIN_ACCEPTED"""
				return False
			if reply_code == 201:
				"""LOGIN_ACCEPTED_NEW_VERSION"""
				return False
			if reply_code == 203:
				"""LOGGED_OUT"""
				return False
			if reply_code == 205:
				"""RESOURCE"""
				return False
			if reply_code == 206:
				"""STATS"""
				return False
			if reply_code == 207:
				"""TOP"""
				return False
			if reply_code == 208:
				"""UPTIME"""
				return False
			if reply_code == 209:
				"""ENCRYPTION_ENABLED"""
				return False
			if reply_code == 210:
				"""MYLIST_ENTRY_ADDED"""
				return False
			if reply_code == 211:
				"""MYLIST_ENTRY_DELETED"""
				return False
			if reply_code == 214:
				"""ADDED_FILE"""
				return False
			if reply_code == 215:
				"""ADDED_STREAM"""
				return False
			if reply_code == 217:
				"""EXPORT_QUEUED"""
				return False
			if reply_code == 218:
				"""EXPORT_CANCELLED"""
				return False
			if reply_code == 219:
				"""ENCODING_CHANGED"""
				return False
			if reply_code == 220:
				"""FILE"""
				return False
			if reply_code == 221:
				"""MYLIST"""
				return False
			if reply_code == 222:
				"""MYLIST_STATS"""
				return False
			if reply_code == 223:
				"""WISHLIST"""
				return False
			if reply_code == 224:
				"""NOTIFICATION"""
				return False
			if reply_code == 225:
				"""GROUP_STATUS"""
				return False
			if reply_code == 226:
				"""WISHLIST_ENTRY_ADDED"""
				return False
			if reply_code == 227:
				"""WISHLIST_ENTRY_DELETED"""
				return False
			if reply_code == 228:
				"""WISHLIST_ENTRY_UPDATED"""
				return False
			if reply_code == 229:
				"""MULTIPLE_WISHLIST"""
				return False
			if reply_code == 230:
				"""ANIME"""
				return False
			if reply_code == 231:
				"""ANIME_BEST_MATCH"""
				return False
			if reply_code == 232:
				"""RANDOM_ANIME"""
				return False
			if reply_code == 233:
				"""ANIME_DESCRIPTION"""
				return False
			if reply_code == 234:
				"""REVIEW"""
				return False
			if reply_code == 235:
				"""CHARACTER"""
				return False
			if reply_code == 236:
				"""SONG"""
				return False
			if reply_code == 237:
				"""ANIMETAG"""
				return False
			if reply_code == 238:
				"""CHARACTERTAG"""
				return False
			if reply_code == 240:
				"""EPISODE"""
				return False
			if reply_code == 243:
				"""UPDATED"""
				return False
			if reply_code == 244:
				"""TITLE"""
				return False
			if reply_code == 245:
				"""CREATOR"""
				return False
			if reply_code == 246:
				"""NOTIFICATION_ENTRY_ADDED"""
				return False
			if reply_code == 247:
				"""NOTIFICATION_ENTRY_DELETED"""
				return False
			if reply_code == 248:
				"""NOTIFICATION_ENTRY_UPDATE"""
				return False
			if reply_code == 249:
				"""MULTIPLE_NOTIFICATION"""
				return False
			if reply_code == 250:
				"""GROUP"""
				return False
			if reply_code == 251:
				"""CATEGORY"""
				return False
			if reply_code == 253:
				"""BUDDY_LIST"""
				return False
			if reply_code == 254:
				"""BUDDY_STATE"""
				return False
			if reply_code == 255:
				"""BUDDY_ADDED"""
				return False
			if reply_code == 256:
				"""BUDDY_DELETED"""
				return False
			if reply_code == 257:
				"""BUDDY_ACCEPTED"""
				return False
			if reply_code == 258:
				"""BUDDY_DENIED"""
				return False
			if reply_code == 260:
				"""VOTED"""
				return False
			if reply_code == 261:
				"""VOTE_FOUND"""
				return False
			if reply_code == 262:
				"""VOTE_UPDATED"""
				return False
			if reply_code == 263:
				"""VOTE_REVOKED"""
				return False
			if reply_code == 265:
				"""HOT_ANIME"""
				return False
			if reply_code == 266:
				"""RANDOM_RECOMMENDATION"""
				return False
			if reply_code == 267:
				"""RANDOM_SIMILAR"""
				return False
			if reply_code == 270:
				"""NOTIFICATION_ENABLED"""
				return False
			if reply_code == 281:
				"""NOTIFYACK_SUCCESSFUL_MESSAGE"""
				return False
			if reply_code == 282:
				"""NOTIFYACK_SUCCESSFUL_NOTIFIATION"""
				return False
			if reply_code == 290:
				"""NOTIFICATION_STATE"""
				return False
			if reply_code == 291:
				"""NOTIFYLIST"""
				return False
			if reply_code == 292:
				"""NOTIFYGET_MESSAGE"""
				return False
			if reply_code == 293:
				"""NOTIFYGET_NOTIFY"""
				return False
			if reply_code == 294:
				"""SENDMESSAGE_SUCCESSFUL"""
				return False
			if reply_code == 295:
				"""USER_ID"""
				return False
			if reply_code == 297:
				"""CALENDAR"""
				return False
			if reply_code == 300:
				"""PONG"""
				return False
			if reply_code == 301:
				"""AUTHPONG"""
				return False
			if reply_code == 305:
				"""NO_SUCH_RESOURCE"""
				return False
			if reply_code == 309:
				"""API_PASSWORD_NOT_DEFINED"""
				return False
			if reply_code == 310:
				"""FILE_ALREADY_IN_MYLIST"""
				return False
			if reply_code == 311:
				"""MYLIST_ENTRY_EDITED"""
				return False
			if reply_code == 312:
				"""MULTIPLE_MYLIST_ENTRIES"""
				return False
			if reply_code == 313:
				"""WATCHED"""
				return False
			if reply_code == 314:
				"""SIZE_HASH_EXISTS"""
				return False
			if reply_code == 315:
				"""INVALID_DATA"""
				return False
			if reply_code == 316:
				"""STREAMNOID_USED"""
				return False
			if reply_code == 317:
				"""EXPORT_NO_SUCH_TEMPLATE"""
				return False
			if reply_code == 318:
				"""EXPORT_ALREADY_IN_QUEUE"""
				return False
			if reply_code == 319:
				"""EXPORT_NO_EXPORT_QUEUED_OR_IS_PROCESSING"""
				return False
			if reply_code == 320:
				"""NO_SUCH_FILE"""
				return False
			if reply_code == 321:
				"""NO_SUCH_ENTRY"""
				return False
			if reply_code == 322:
				"""MULTIPLE_FILES_FOUND"""
				return False
			if reply_code == 323:
				"""NO_SUCH_WISHLIST"""
				return False
			if reply_code == 324:
				"""NO_SUCH_NOTIFICATION"""
				return False
			if reply_code == 325:
				"""NO_GROUPS_FOUND"""
				return False
			if reply_code == 330:
				"""NO_SUCH_ANIME"""
				return False
			if reply_code == 333:
				"""NO_SUCH_DESCRIPTION"""
				return False
			if reply_code == 334:
				"""NO_SUCH_REVIEW"""
				return False
			if reply_code == 335:
				"""NO_SUCH_CHARACTER"""
				return False
			if reply_code == 336:
				"""NO_SUCH_SONG"""
				return False
			if reply_code == 337:
				"""NO_SUCH_ANIMETAG"""
				return False
			if reply_code == 338:
				"""NO_SUCH_CHARACTERTAG"""
				return False
			if reply_code == 340:
				"""NO_SUCH_EPISODE"""
				return False
			if reply_code == 343:
				"""NO_SUCH_UPDATES"""
				return False
			if reply_code == 344:
				"""NO_SUCH_TITLES"""
				return False
			if reply_code == 345:
				"""NO_SUCH_CREATOR"""
				return False
			if reply_code == 350:
				"""NO_SUCH_GROUP"""
				return False
			if reply_code == 351:
				"""NO_SUCH_CATEGORY"""
				return False
			if reply_code == 355:
				"""BUDDY_ALREADY_ADDED"""
				return False
			if reply_code == 356:
				"""NO_SUCH_BUDDY"""
				return False
			if reply_code == 357:
				"""BUDDY_ALREADY_ACCEPTED"""
				return False
			if reply_code == 358:
				"""BUDDY_ALREADY_DENIED"""
				return False
			if reply_code == 360:
				"""NO_SUCH_VOTE"""
				return False
			if reply_code == 361:
				"""INVALID_VOTE_TYPE"""
				return False
			if reply_code == 362:
				"""INVALID_VOTE_VALUE"""
				return False
			if reply_code == 363:
				"""PERMVOTE_NOT_ALLOWED"""
				return False
			if reply_code == 364:
				"""ALREADY_PERMVOTED"""
				return False
			if reply_code == 365:
				"""HOT_ANIME_EMPTY"""
				return False
			if reply_code == 366:
				"""RANDOM_RECOMMENDATION_EMPTY"""
				return False
			if reply_code == 367:
				"""RANDOM_SIMILAR_EMPTY"""
				return False
			if reply_code == 370:
				"""NOTIFICATION_DISABLED"""
				return False
			if reply_code == 381:
				"""NO_SUCH_ENTRY_MESSAGE"""
				return False
			if reply_code == 382:
				"""NO_SUCH_ENTRY_NOTIFICATION"""
				return False
			if reply_code == 392:
				"""NO_SUCH_MESSAGE"""
				return False
			if reply_code == 393:
				"""NO_SUCH_NOTIFY"""
				return False
			if reply_code == 394:
				"""NO_SUCH_USER"""
				return False
			if reply_code == 397:
				"""CALENDAR_EMPTY"""
				return False
			if reply_code == 399:
				"""NO_CHANGES"""
				return False
			if reply_code == 403:
				"""NOT_LOGGED_IN"""
				return False
			if reply_code == 410:
				"""NO_SUCH_MYLIST_FILE"""
				return False
			if reply_code == 411:
				"""NO_SUCH_MYLIST_ENTRY"""
				return False
			if reply_code == 412:
				"""MYLIST_UNAVAILABLE"""
				return False
			if reply_code == 500:
				"""LOGIN_FAILED"""
				return False
			if reply_code == 501:
				"""LOGIN_FIRST"""
				return False
			if reply_code == 502:
				"""ACCESS_DENIED"""
				return False
			if reply_code == 503:
				"""CLIENT_VERSION_OUTDATED"""
				return False
			if reply_code == 504:
				"""CLIENT_BANNED"""
				return False
			if reply_code == 505:
				"""ILLEGAL_INPUT_OR_ACCESS_DENIED"""
				return False
			if reply_code == 506:
				"""INVALID_SESSION"""
				return False
			if reply_code == 509:
				"""NO_SUCH_ENCRYPTION_TYPE"""
				return False
			if reply_code == 519:
				"""ENCODING_NOT_SUPPORTED"""
				return False
			if reply_code == 555:
				"""BANNED"""
				return False
			if reply_code == 598:
				"""UNKNOWN_COMMAND"""
				return False
			if reply_code == 600:
				"""INTERNAL_SERVER_ERROR"""
				return False
			if reply_code == 601:
				"""ANIDB_OUT_OF_SERVICE"""
				return False
			if reply_code == 602:
				"""SERVER_BUSY"""
				return False
			if reply_code == 603:
				"""NO_DATA"""
				return False
			if reply_code == 604:
				"""TIMEOUT - DELAY AND RESUBMIT"""
				return False
			if reply_code == 666:
				"""API_VIOLATION"""
				return False

			if reply_code == 701:
				"""PUSHACK_CONFIRMED"""
				return False
			if reply_code == 702:
				"""NO_SUCH_PACKET_PENDING"""
				return False
			else:
				"""some unknown return code"""
				return False
		except:
			print("ERROR WHILE CODEPARSING THIS STRING: " + tmp)
			return False
