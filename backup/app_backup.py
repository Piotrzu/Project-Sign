from crypt import methods
from flask import Flask, render_template, request, flash, make_response, session
from flask_session import Session
from functions.rsa import *
from functions.TRNG import generateNumbers, getStatistics
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA3_224, SHA3_256, SHA3_384, SHA3_512
from Crypto.Hash import SHA256
import binascii
import hashlib

app = Flask(__name__)
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
    if 'cookie_message' in request.cookies:
        cookieMessage = request.cookies.get('cookie_message')
        return render_template("index.html", gen_new_values_View = True, cookieMessage = cookieMessage)
    return render_template("index.html", gen_new_values_View = True)

@app.route("/new_trng_values", methods = ['POST'])
def generate_new_trng_values():
    amount = request.form['gen_trng_input']
    generateNumbers(int(amount))

    if 'cookie_message' in request.cookies:
        cookieMessage = request.cookies.get('cookie_message')
        return render_template("index.html", cookieMessage = cookieMessage, done = True)

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

    session['messageSession'] = original_message
    session['hashedMessageSession'] = hashed_original_message.hexdigest()
    response = make_response(render_template('index.html', hashed_original_message = hashed_original_message))
    response.set_cookie('cookie_hashedMessage', hashed_original_message.hexdigest())
    response.set_cookie('cookie_message', original_message)
    return response

@app.route("/sign_message")
def sign():
    if 'cookie_message' and 'cookie_hashedMessage' in request.cookies:
        cookieMessage = request.cookies.get('cookie_message')
        cookieHashedMessage = request.cookies.get('cookie_hashedMessage')
        
        # RSA Signing
        rsa_keys = generateRSAKeys()
        global public_rsaKey
        public_rsaKey = getPublicRsaKey(rsa_keys)
        session['publicRSAKeySession'] = str(public_rsaKey.exportKey('PEM'))
        new_SignedMessage = signMessage(hashed_original_message, rsa_keys)

        session['signedMessage'] = str(cookieMessage)
        session['isSignedMessageSession'] = True
        session['signatureSession'] = new_SignedMessage
        session['signatureHumanSession'] = binascii.hexlify(new_SignedMessage).__str__()

        return render_template("index.html", cookieMessage = cookieMessage, cookieHashedMessage = cookieHashedMessage, publicRsaKey = public_rsaKey, signed = True)
    return render_template("index.html")

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
    #generateNumbers()
    [valuesList, probList, entropy] = getStatistics()

    labels = [idx for idx, x in enumerate(valuesList)]
    values = [row for row in valuesList]
    print(entropy)

    return render_template("statistics.html", labels = labels, values = values, entropy = entropy)

@app.route("/check_validity", methods=["POST"])
def displayTRNG():
    cooked_message = request.cookies.get('cookie_message')
    return '<h1>welcome ' + cooked_message + '</h1>'
    #data = generateRSAKeys()
    #flash("Hi " + request.form['message_input'] + " thats your number.")
    #return render_template("index.html",  random_values = generatedTRNGValues, trng=True)

# @app.route("/test")
# def test():
#     # data = generateRSAKeys()
#     #return "<h1>generateRSAKeys()</h1>"
#     return render_template("index.html", random_values = data, rsa=True)




# @app.route("/")
# def index():
#     flash('Testing flash alert!')
#     if 'cookie_message' and 'cookie_hashedMessage' in request.cookies:
#         cookieMessage = request.cookies.get('cookie_message')
#         cookieHashedMessage = request.cookies.get('cookie_hashedMessage')
#         return render_template("index.html", cookieMessage = cookieMessage, cookieHashedMessage = cookieHashedMessage)
#     return render_template("index.html")




# @app.route('/hash_message', methods=['POST'])
# def sha_encryption():
#     original_message = request.form['message_input']
#     sha_size = request.form['hash_size_input']
#     # SHA encryption 
#     global hashed_original_message
#     hashed_original_message = hashMessage(original_message, int(sha_size))

#     session['messageSession'] = original_message
#     session['hashedMessageSession'] = hashed_original_message.hexdigest()
#     response = make_response(render_template('index.html', hashed_original_message = hashed_original_message))
#     response.set_cookie('cookie_hashedMessage', hashed_original_message.hexdigest())
#     response.set_cookie('cookie_message', original_message)
#     return response