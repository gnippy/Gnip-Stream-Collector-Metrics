#!/usr/bin/env python
#
#   scott hendrickson (shendrickson@gnipcentral.com)
#      2011-08-23 09:53:47.873347
#
#####################
__author__ = 'scott hendrickson'

import sys
from SaveThread import SaveThread
import json
import redis
import re

#####################

engstoplist = ["un", "da", "se", "ap", "el", "morreu", "en", "la", "que", "ll", "don", "ve", "de", "gt", "lt", "com", "ly", "co", "re", "rt", "http","a","able","about","across","after","all","almost","also","am","among","an","and","any","are","as","at","be","because","been","but","by","can","cannot","could","dear","did","do","does","either","else","ever","every","for","from","get","got","had","has","have","he","her","hers","him","his","how","however","i","if","in","into","is","it","its","just","least","let","like","likely","may","me","might","most","must","my","neither","no","nor","not","of","off","often","on","only","or","other","our","own","rather","said","say","says","she","should","since","so","some","than","that","the","their","them","then","there","these","they","this","tis","to","too","twas","us","wants","was","we","were","what","when","where","which","while","who","whom","why","will","with","would","yet","you","your"]

# ascii only !
spanstoplist = [ "un", "una" ,"unas" ,"unos" ,"uno" ,"sobre" ,"todo" ,"tambien" ,"tras" ,"otro" ,"algun" ,"alguno" ,"alguna" ,"algunos" ,"algunas" ,"ser" ,"es" ,"soy" ,"eres" ,"somos" ,"sois" ,"estoy" ,"esta" ,"estamos" ,"estais" ,"estan" ,"como" ,"en" ,"para" ,"atras" ,"porque" ,"porque" ,"estado" ,"estaba" ,"ante" ,"antes" ,"siendo" ,"ambos" ,"pero" ,"por" ,"poder" ,"puede" ,"puedo" ,"podemos" ,"podeis" ,"pueden" ,"fui" ,"fue" ,"fuimos" ,"fueron" ,"hacer" ,"hago" ,"hace" ,"hacemos" ,"haceis" ,"hacen" ,"cada" ,"fin" ,"incluso" ,"primero	desde" ,"conseguir" ,"consigo" ,"consigue" ,"consigues" ,"conseguimos" ,"consiguen" ,"ir" ,"voy" ,"va" ,"vamos" ,"vais" ,"van" ,"vaya" ,"gueno" ,"ha" ,"tener" ,"tengo" ,"tiene" ,"tenemos" ,"teneis" ,"tienen" ,"el" ,"la" ,"lo" ,"las" ,"los" ,"su" ,"aqui" ,"mio" ,"tuyo" ,"ellos" ,"ellas" ,"nos" ,"nosotros" ,"vosotros" ,"vosotras" ,"si" ,"dentro" ,"solo" ,"solamente" ,"saber" ,"sabes" ,"sabe" ,"sabemos" ,"sabeis" ,"saben" ,"ultimo" ,"largo" ,"bastante" ,"haces" ,"muchos" ,"aquellos" ,"aquellas" ,"sus" ,"entonces" ,"tiempo" ,"verdad" ,"verdadero" ,"verdadera" ,"cierto" ,"ciertos" ,"cierta" ,"ciertas" ,"intentar" ,"intento" ,"intenta" ,"intentas" ,"intentamos" ,"intentais" ,"intentan" ,"dos" ,"bajo" ,"arriba" ,"encima" ,"usar" ,"uso" ,"usas" ,"usa" ,"usamos" ,"usais" ,"usan" ,"emplear" ,"empleo" ,"empleas" ,"emplean" ,"ampleamos" ,"empleais" ,"valor" ,"muy" ,"era" ,"eras" ,"eramos" ,"eran" ,"modo" ,"bien" ,"cual" ,"cuando" ,"donde" ,"mientras" ,"quien" ,"con" ,"entre" ,"sin" ,"trabajo" ,"trabajar" ,"trabajas" ,"trabaja" ,"trabajamos" ,"trabajais" ,"trabajan" ,"podria" ,"podrias" ,"podriamos" ,"podrian" ,"podriais","yo" ,"aquel"]


# reduce this when other languages not needed
stoplist = engstoplist + spanstoplist

# looking for most common terms so set time to live in redis store in seconds
ttl = 90

#####################

class Redis(SaveThread):

    def saveAs(self, buffer):
        self.logger.debug("CountRules started")
	# You may want to "flushall" before running this to start with a clean redis cache
	rs = redis.Redis("localhost")
	for act in buffer.split("\n"):
		self.logger.debug(str(act))
		if act.strip() is None or act.strip() == '':
			continue
		actJson = json.loads(act)
		if "gnip" in actJson:
			if "matching_rules" in actJson["gnip"]:
				for mr in actJson["gnip"]["matching_rules"]:
					self.logger.debug("inc rule (%s)"%str(mr["value"]))
					# Redis store of rule match counts
					key = "["+mr["value"]+"]"
					rs.incr(key)
					rs.incr("TotalRuleMatchCount")
			else:
				self.logger.debug("matching_rules missing")
		else:
			self.logger.debug("gnip tag missing")

		if "body" in actJson:
			for t in re.split("\W+", actJson["body"]):
				tok = t.lower()
				if tok not in stoplist and len(tok) > 2:
					self.logger.debug("inc (%s)"%tok)
					# Redis store of token counts
					rs.incr(tok)
					rs.expire(tok, ttl)
					rs.incr("TotalTokensCount")
        sys.exit(0)
