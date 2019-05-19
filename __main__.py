from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bitcoinrpc.authproxy import AuthServiceProxy
from random import seed, randint
from os import urandom
import hashlib, logging
from config import *

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Hashing de (string + salt) en algoritmo sha256
def hash(string):
	sha = hashlib.sha256()
	template = (str(string) + salt).encode('utf-8')
	sha.update(template)

	return sha.hexdigest()

def getaddress(name):
	addressList = rpc.getaddressesbyaccount(name)

	if len(addressList) == 0:
		address = rpc.getnewaddress(name)
	else:
		address = addressList[0]

	return address

def start(bot, update):
	user = update.message.from_user

	msg = "Holi, soy Chungungo :D"
	msg += "\nPuedes interactuar conmigo con estos simples comandos:"
	msg += "\n\n/address te permite crear una dirección especifica para tu usuario de Telegram, la cual sirve para enviar o recibir Keplers."
	msg += "\n\n/balance enseña la cantidad de Kepler que tienes dentro de esa dirección"
	msg += "\n\nel comando /send puedes enviar Keplers hacia otras direcciones."
	msg += " Por ejemplo, si deseas enviarle 100 KPL a la dirección KfBifAmAK3h9Ke4wE2auXaEbfPqeMV44GQ debes usar el comando de la siguiente manera:"
	msg += "\n\n/send 100 KfBifAmAK3h9Ke4wE2auXaEbfPqeMV44GQ"
	msg += "\n\nademás, puedes ver informacion de masternodes con /masternode IP"

	logger.info("start(%i)" % user.id)
	update.message.reply_text("%s" % msg)	

# Enviar KPL
def send(bot, update):
	user = update.message.from_user
	userHash = hash(user.id)
	balance = float(rpc.getbalance(userHash))

	try:
		msgSplit = update.message.text.split(" ")

		amount = float(msgSplit[1])
		receptor = msgSplit[2]

		if not len(receptor) == 34 and receptor[0] == 'K':
			sending = "Address inválida"
		else:
			if not balance > amount:
				sending = "Balance insuficiente"
			else:
				if not amount > 0:
					sending	= "Monto inválido"
				else:
					sending = rpc.sendfrom(userHash, receptor, float(amount))
					sending = "txid: " + sending

	except:
		amount = 0.0
		receptor = "invalid"
		sending = "syntax error\nUSO: /send monto address"

	logger.info("send(%i, %f, %s) => %s" % (user.id, amount, receptor, sending))
	update.message.reply_text("%s" % sending)		


# Dado
""" def dice(bot, update):
	user = update.message.from_user
	userHash = hash(user.id)
	userAddress = getaddress(userHash)
	userBalance = float(rpc.getbalance(userHash))
	
	try:
		msgSplit = update.message.text.split(" ")
		bet = float(msgSplit[1])

		if not bet > 0.001:
			result = "apuesta inválida"
		else:
			if not bet < userBalance or not userBalance > 0.001:
				result = "balance insuficiente"
			else:
				botAddress = getaddress("chungungo")
				botBalance = float(rpc.getbalance("chungungo"))

				if not botBalance > bet:
					result = "No tengo tantas KPLuKPLs :c"
				else:
					seed(repr(urandom(64)))
					dice = randint(0,100)
					if dice > (50 + 3):# 3% house edge
						result = "Ganaste %f KPL !\nNúmero: %i" % (bet, dice)
						rpc.sendfrom("chungungo", userAddress, bet)
					else:
						if dice == (50 + 3):
							result = "BONUS x3 !! Ganaste %f KPL\nNúmero: 50" % (bet*3)
							rpc.sendfrom("chungungo", userAddress, bet*3)

						else:
							result = "Perdiste %f KPL\nNúmero: %i" % (bet, dice)
							rpc.sendfrom(userHash, botAddress, bet)
	except:
		bet = 0.0
		result = "syntax error\nUSO: /dado apuesta"
	
	logger.info("dice(%i, %f) => %s" % (user.id, bet, result))
	update.message.reply_text("%s" % result)	 """	


# Mostrar saldo y address de chungungo
def info(bot, update):
	address = getaddress("chungungo")
	balance = float(rpc.getbalance("chungungo"))

	logger.info("info() => (%s, %f)" % (address, balance))
	update.message.reply_text("Address: %s\nBalance: %f" % (address, balance))		


# Generar solo 1 address por usuario (user.id)
def address(bot, update):
	user = update.message.from_user
	userHash = hash(user.id)

	address = getaddress(userHash)

	logger.info("address(%i) => %s" % (user.id, address))
	update.message.reply_text("%s" % address)


# Mostrar balance de usuario
def balance(bot, update):
	user = update.message.from_user
	userHash = hash(user.id)

	balance = float(rpc.getbalance(userHash))

	logger.info("balance(%i) => %f" % (user.id, balance))
	update.message.reply_text("{0:.8f} CHA".format(balance))

# Información de Masternodes
def masternode(bot, update):

	msgSplit = update.message.text.split(" ")
	if len(msgSplit) == 1:
		address = msgSplit[1]

		if len(address) > 35 or len(address) < 8:
			sending = "IP inválida"
		else:
			info = rpc.masternodelist('json', address)
			if len(info) == 1:
				info = list(info.values())[0]['status']
				if info == "ENABLED":
					sending = "✅ masternode activo"
				elif info == "SENTINEL_PING_EXPIRED":
					sending = "❌ tu masternode necesita Sentinel para funcionar"
				else:
					sending = "❌ hay un problema con tu masternode, revisalo"
			else:
				sending = "IP inválida %s" % str(len(info))

		logger.info("masternode(%s) => %s" % (address, info))
		update.message.reply_text("%s" % sending)		
	else:
		sending = "syntax error\nUSO: /masternode IP"
		logger.info("masternode(%s) => %s" % ("none", "none"))
		update.message.reply_text("%s" % sending)		

""" # Información de la red
def red(bot, update):
	info = rpc.getmininginfo()

	difficulty = float(info['difficulty'])
	blocks = info['blocks']
	power = info['networkhashps'] / 1000000.0

	delta = difficulty * 2**32 / float(info['networkhashps']) / 60 / 60.0

	logger.info("red() => (%i, %f, %f, %i)" % (blocks, difficulty, power, delta))

	if delta < 1:
		delta = str(round(delta*60, 3)) + " minutos"
	else:
		delta = str(round(delta, 3)) + " horas"

	msg = "Bloques: %i\nDificultad: %f\nHashing Power: %f Mh/s\n\nEl siguiente bloque se creará en %s"

	update.message.reply_text(msg % (blocks, difficulty, power, delta)) """

def error(bot, update, error):
	logger.warning('Update: "%s" - Error: "%s"', update, error)


def main():
	global rpc

	# Configuración
	rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:%i"%(RPCuser, RPCpassword, RPCport))
	updater = Updater(token)

	# Creación de address para chungungo
	getaddress("chungungo")

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Listado de comandos
	dp.add_handler(CommandHandler("address", address))
	dp.add_handler(CommandHandler("balance", balance))
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", start))
	dp.add_handler(CommandHandler("send", send))
	dp.add_handler(CommandHandler("info", info))
	#dp.add_handler(CommandHandler("dice", dice))
	dp.add_handler(CommandHandler("masternode", masternode))
	#dp.add_handler(CommandHandler("red", red))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	logger.info("Init")

	updater.idle()


if __name__ == '__main__':
	main()
