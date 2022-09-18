from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA3_224, SHA3_256, SHA3_384, SHA3_512
from time import gmtime, strftime

def generateRSAKeys():
    with open('results.txt', 'rb') as trngBinValues:
        keyPair = RSA.generate(1024, trngBinValues.read)
    return keyPair

def getPublicRsaKey(rsaKeys):
    return rsaKeys.publickey()

def hashMessage(message, hashSize = 256):
    if (hashSize == 224):
        hashedMessage = SHA3_224.new(message.encode())
    elif (hashSize == 384):
        hashedMessage = SHA3_384.new(message.encode())
    elif (hashSize == 512):
        hashedMessage = SHA3_512.new(message.encode())
    else:
        hashedMessage = SHA3_256.new(message.encode())
    print(hashedMessage)
    return hashedMessage

def signMessage(hashedMessage, rsaKeys):
    signer = PKCS115_SigScheme(rsaKeys)
    signedMessage = signer.sign(hashedMessage)
    return signedMessage

def verifySignature(hashedMessage, signedMessage, publicRsaKey):
    rsa = PKCS115_SigScheme(publicRsaKey)
    try:
        rsa.verify(hashedMessage, signedMessage)
        return True
    except:
        return False
    
def saveHash(originalMessage, hashedMessage):
    historyFile = open('historicalData.txt', 'a')
    historyFile.writelines("[HASHED] Original message: " + " " +  originalMessage + '\n' +  " Hashed message: " + hashedMessage + " " + '\n'+ "Date:" +  strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '\n')
    historyFile.close()

def saveSign(originalMessage, signedMessage):
    historyFile = open('historicalData.txt', 'a')
    historyFile.writelines("[SIGNED] Original message: " + " " +  originalMessage + '\n' +  " Signature: " + signedMessage + " " + '\n'+ "Date:" +  strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '\n')
    historyFile.close()