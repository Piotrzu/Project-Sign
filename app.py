from crypt import methods
from flask import Flask, render_template, request, flash, make_response, session
from flask_session import Session
from functions.rsa import *
from os.path import exists
from functions.TRNG import generateNumbers, getStatistics
import binascii

app = Flask(__name__)
hashed_original_message = ""
app.secret_key = "super secret key"
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/enter_new_message")
def enterNewMessage():
    return render_template("index.html", enterNewMessage = True)

@app.route("/generate_trng", methods = ['POST'])
def generate_trng():
    return render_template("index.html", gen_new_values_View = True)

@app.route("/new_trng_values", methods = ['POST'])
def generate_new_trng_values():
    amount = request.form['gen_trng_input']
    generateNumbers(int(amount))
    return render_template("index.html", done = True)

@app.route('/rsa_keypair', methods=["POST", "GET"])
def generate_rsa_keys():
    generated_keys = generateRSAKeys()
    original_message = request.form['message_input']
    return render_template("rsa.html", original_message = original_message, rsa_keys = generated_keys)

@app.route('/hash_message', methods=['POST'])
def sha_encryption():
    original_message = request.form['message_input']
    sha_size = request.form['hash_size_input']

    # SHA encryption 
    global hashed_original_message
    hashed_original_message = hashMessage(original_message, int(sha_size))
    saveHash(str(original_message), hashed_original_message.hexdigest())
    session['messageSession'] = original_message
    session['hashedMessageSession'] = hashed_original_message.hexdigest()
    return render_template("index.html", hashed_original_message = hashed_original_message)

@app.route("/sign_message", methods=['POST'])
def sign():
    if(hashed_original_message):
        # RSA Signing
        rsa_keys = generateRSAKeys()
        global public_rsaKey
        public_rsaKey = getPublicRsaKey(rsa_keys)
        session['publicRSAKeySession'] = str(public_rsaKey.exportKey('PEM'))
        new_SignedMessage = signMessage(hashed_original_message, rsa_keys)
        session['signedMessage'] = session.get('messageSession')
        session['isSignedMessageSession'] = True
        session['signatureSession'] = new_SignedMessage
        session['signatureHumanSession'] = binascii.hexlify(new_SignedMessage).__str__() 
        saveSign(session.get('messageSession'), binascii.hexlify(new_SignedMessage).__str__())
        return render_template("index.html", publicRsaKey = public_rsaKey, signed = True)
    else:
        return render_template("index.html", hashedMessageError = True)
        

@app.route("/check")
def checkValidity():
    signed_message = session.get('signatureSession')
    check_validity = verifySignature(hashed_original_message, signed_message, public_rsaKey)

    if (check_validity):
        return render_template("valid.html")
    else:
        return render_template("invalid.html")

@app.route("/stats", methods = ['POST'])
def statistics():
    [valuesList, probList, entropy] = getStatistics()

    labels = [idx for idx, x in enumerate(valuesList)]
    values = [row for row in valuesList]

    return render_template("statistics.html", labels = labels, values = values, entropy = entropy)

@app.route("/historical")
def historical():
    filePath='historicalData.txt'
    data = []
    if(exists(filePath) == False):
        historyFile = open('historicalData.txt', 'a')
    
    with open(filePath) as fp:
        line = fp.readline()
        cnt = 0
        while line:
            data.append(line.strip())
            line = fp.readline()
            cnt += 1
    return render_template("historical.html", historicalData = data, length = len(data))