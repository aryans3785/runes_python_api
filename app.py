from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from mongoengine import connect
import requests
from bson.objectid import ObjectId
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import datetime
import json
import math
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from mongoengine.queryset.visitor import Q
from functools import wraps
from model.runeInfo import Rune
from model.runeListing import RuneListing
from flask_limiter import Limiter
from flask_restx import Api, Resource, fields
from flask_limiter.util import get_remote_address


load_dotenv()

app = Flask(__name__)
api = Api(app, version='1.0', title='Rune API', description='APIs to manage runes' , doc = '/docs')

# Define a function to create and configure the Limiter object
def create_limiter(app):
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100 per day", "10 per hour"]
    )
    limiter.init_app(app)
    return limiter

# Use the factory function to create and configure the Limiter object
limiter = create_limiter(app)
cors = CORS(app, origins=['https://mint-iz3y.onrender.com/en/mint-runes', 'https://mint-iz3y.onrender.com/', 'https://mint-iz3y.onrender.com', 'mint-iz3y.onrender.com/','localhost:3000','https://localhost:3000', 'https://development-3mci.onrender.com/' , 'http://localhost:3000', 'https://rune-frontend.onrender.com', 'https://rune-frontend-2.onrender.com', 'https://development.runepro.com', 'https://development.onrender.com', 'https://rune-dashboard.onrender.com', 'http://localhost:5500/', 'http://localhost:8888', 'https://runepro-test.vercel.app', 'https://runepro.com', 'https://www.runepro.com', 'https://testnet.runepro.com',  'https://rune-frontend-1.onrender.com', 'https://development-3mci.onrender.com/'])

URL = "https://testnet-backend-ivoa.onrender.com"

uri = os.getenv("MONGO_URI")
db = os.getenv("DB")

# Define a dictionary to store API keys and their associated users or clients
api_keys = {
    'api_key': 'rune@python'
}


# Decorator function to require API key authentication
def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != api_keys['api_key']:
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)  # Call the original function without passing the user argument
    return wrapper

error_missingInfo = "RP101"
error_missingInscription = "RP102"
error_offer_already_exist ="RP106"
error_offer_not_exist= "RP108"
error_offer_is_invalid="RP109"
error_invalid = "RP103"
error_wallet = "RP104"
error_misc = "RP105"
error_not_enough_balance = "RP107"
error_missingSetup = "RP110"

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_URI"),
    integrations=[FlaskIntegration()],
    release=os.environ.get("VERSION"),
    enable_tracing=True,
    
)
def check_db_connection():
    try:
        # Connect to MongoDB using MongoEngine
        connect(
            db=db,  # replace with your database name
            host=uri,
            tlsCAFile=certifi.where()
        )
        print("Connected to DB. Server status: MongoDB")
    except Exception as e:
        print("Failed to connect to DB:", str(e))

check_db_connection()


@app.route('/throwerror')
def throw_error(): 
    1/0  # raises an error
    return "<p>Hello, World!</p>"

@app.route('/getfeerates')
def GetFeeRates():
    return requests.get(URL+"/getfeerates").json()

@app.route('/')
def hello_world():
    return 'Hello, friend!'

@app.route('/runes/points', methods=['POST'])
def getPoints():
    args = request.get_json()
    addr = args['OrdinalAddress']
    points = pymongo.db.points.find_one({'Address': addr})
    if points==None:
        return jsonify({'points': 0})
    return jsonify({'points': points['Points']})

# @app.route('/runes', methods=['POST'])
# def RuneIndex():
#     runes = pymongo.db.runeInfo.find({'Mintable':True},{ "_id": 0})
#     runelist = [a for a in runes]
#     runelist.reverse()
#     runes = pymongo.db.runeInfo.find({'Mintable':False},{ "_id": 0})
#     runelist2 = [a for a in runes]
#     runelist += runelist2
#     return runelist

# Define a model for the request parameters
pagination_params = api.model('Pagination', {
    'page': fields.Integer(description='Page number', example=1, default=1),
    'limit': fields.Integer(description='Number of items per page', example=10, default=10),
    'search': fields.String(description='Search query', example='example search term', default='')
})

# Define a model for the response metadata
metadata_model = api.model('Metadata', {
    'pageNumber': fields.Integer(description='Current page number'),
    'perPage': fields.Integer(description='Number of items per page'),
    'pageCount': fields.Integer(description='Number of items on the current page'),
    'totalCount': fields.Integer(description='Total number of items'),
    'numOfPages': fields.Integer(description='Total number of pages')
})

# Define the model for a single rune
rune_model = api.model('Rune', {
    '_id': fields.String(description='Rune ID'),
    'SpacedRune': fields.String(description='Spaced rune string'),
    'Created': fields.DateTime(description='Creation date'),
    'Divisibility': fields.Integer(description='Divisibility'),
    'EtchTx': fields.String(description='Etch transaction'),
    'LimitPerMint': fields.Integer(description='Limit per mint'),
    'MaxMintNumber': fields.Integer(description='Maximum mint number'),
    'MintEndAfter': fields.DateTime(description='Mint end after'),
    'MintEndBlock': fields.Integer(description='Mint end block'),
    'MintStartBlock': fields.Integer(description='Mint start block'),
    'Minted': fields.Integer(description='Minted count'),
    'Premine': fields.Integer(description='Premine count'),
    'Progress': fields.Float(description='Progress'),
    'RuneID': fields.String(description='Rune ID'),
    'Supply': fields.Integer(description='Supply'),
    'Symbol': fields.String(description='Symbol'),
    'Mintable': fields.Boolean(description='Mintable status'),
})

# Define a model for the response data
response_model = api.model('Response', {
    'runes': fields.List(fields.Nested(rune_model), description='List of runes'),
    'metadata': fields.Nested(metadata_model, description='Metadata for the response')
})


@api.route('/runes')
class RuneResource(Resource):
    @api.doc(description='Get a list of runes with pagination and search')
    @api.expect(pagination_params, validate=True)
    @api.marshal_with(response_model)
    @limiter.limit("5 per minute")
    def post(self):
        try:
            page = int(request.json.get('page', 1))
            limit = int(request.json.get('limit', 10))
            search_query = request.json.get('search','')
            print("search_query", search_query)
            skip = (page - 1) * limit
            regex_query = Q(SpacedRune__icontains=search_query)
            runes = Rune.objects(regex_query).skip(skip).limit(limit)
            # print("runes", runes)
            runelist = []
            for rune in runes:
                rune_dict = rune.to_mongo().to_dict()
                rune_dict['_id'] = str(rune_dict['_id'])
                runelist.append(rune_dict)
                # print("runelist", runelist)
            total_count = Rune.objects(regex_query).count()
            pageNumber = page
            perPage = limit
            pageCount = len(runelist)
            totalCount = total_count
            numOfPages = math.ceil(total_count / limit)
            metadata = {
                "pageNumber": pageNumber,
                "perPage": perPage,
                "pageCount": pageCount,
                "totalCount": totalCount,
                "numOfPages": numOfPages
            }
            response_data = {
                "runes": runelist,
                "metadata": metadata 
            }
            return response_data
        except Exception as e:
            api.abort(500, f"Internal server error: {str(e)}")


@app.route('/rune', methods=['POST'])
def SingleRuneInfo():
    args = request.get_json()
    name = args['rune']
    rune = pymongo.db.runeInfo.find_one({'SpacedRune':name},{ "_id": 0})
    return rune

@app.route('/runes/balance', methods=['POST'])
def balances():
    args = request.get_json()
    addr = args['OrdinalAddress']
    return requests.post(URL+"/runes/balance", json= {'OrdinalAddress':addr}).json()

@app.route('/runes/make-psbt', methods=['POST'])
def makeRunePsbt():
    args = request.get_json()
    try:
        payaddr = args['PaymentAddress']
        ordaddr = args['OrdinalAddress']
        rune = args['rune']
        amount = float(args['amount'])
        price = float(args['price'])
        wallet = args['wallet']
        typ = args['type']
    except:
        return jsonify({'error': "Not enough info", 'code':error_missingInfo})
    return requests.post(URL+"/runes/make-psbt", json=args).json()

@app.route('/runes/make-listing', methods=['POST'])
def makeRuneListing():
    args = request.get_json()
    try:
        payaddr = args['PaymentAddress']
        ordaddr = args['OrdinalAddress']
        rune = args['rune']
        amount = float(args['amount'])
        price = float(args['price'])
        wallet = args['wallet']
        typ = args['type']
        pst = args['psbt']
    except:
        return jsonify({'error': "Not enough info", 'code':error_missingInfo})
    return requests.post(URL+"/runes/make-listing", json=args).json()

@app.route('/runes/complete-listing', methods=['POST'])
def completePsbt():
    args = request.get_json()
    payaddr = args['PaymentAddress']
    ordaddr = args['OrdinalAddress']
    wallet = args['wallet']
    id = args['id']
    if wallet == 'xverse':
        pubkey = args['pubKey']
    return requests.post(URL+"/runes/complete-listing", json=args).json()

# @app.route('/runes/completed', methods=['POST'])
# def completedRune():
#     args = request.get_json()
#     id = args.get('id')
#     txid = args.get('txid')
#     listing = pymongo.db.runelistings.find_one({"_id": ObjectId(id)})
#     if (listing == None):
#         return jsonify({'error': "That listing does not exist.", 'code':error_offer_not_exist})
#     if (listing['valid'] != True):
#         return jsonify({'error':"This listing is no longer valid.", 'code':error_offer_is_invalid})
#     return requests.post(URL+"/runes/completed", json=args).json()

@app.route('/runes/completed', methods=['POST'])
def completedRune():
    args = request.get_json()
    _id = args.get('id')
    txid = args.get('txid')

    # Query for the listing using mongoengine
    listing = RuneListing.objects(_id=_id).first()

    # Error handling
    if listing is None:
        return jsonify({'error': "That listing does not exist.", 'code': error_offer_not_exist})
    if not listing.valid:
        return jsonify({'error': "This listing is no longer valid.", 'code': error_offer_is_invalid})

    # Forward the request if the listing is valid
    return requests.post(URL+"/runes/completed", json=args).json()


@app.route('/runes/listings', methods=['POST'])
def getRuneListings():
    args = request.get_json()
    rune = args.get('rune')
    posts = pymongo.db.runelistings
    listings = []
    for each in posts.find({'valid':True,'rune':rune}):
        listings.append({'id': str(each['_id']),
                        'type': each['type'],
                        'amount': int(each['amount']),
                        'price': int(each['price']),
                        'rune': each['rune'],
                        'symbol':each['symbol'],
                        'OrdinalAddress': each['OrdinalAddress'],
                        'PaymentAddress': each['PaymentAddress'],
                        'CounterOffers': each['CounterOffers']})
    return jsonify(listings)

@app.route('/runes/open-offers', methods=['POST'])
def getOpenRuneOffers():
    args = request.get_json()
    addr = args.get('OrdinalAddress')
    posts = pymongo.db.runelistings
    offers = []
    for each in posts.find({'valid':True,'OrdinalAddress':addr}):
        offers.append({'id': str(each['_id']),
                        'type': each['type'],
                        'amount': int(each['amount']),
                        'price': int(each['price']),
                        'rune': each['rune'],
                        'symbol':each['symbol'],
                        'OrdinalAddress': addr,
                        'PaymentAddress': each['PaymentAddress'],
                        'CounterOffers': each['CounterOffers']})
    return jsonify(offers)

@app.route('/runes/history', methods=['POST'])
def prevRuneSales():
    args = request.get_json()
    rune = args.get('rune')
    sales = pymongo.db.runesales.find({'rune':rune},{ "_id": 0}).sort('time', -1)
    return jsonify([a for a in sales])

@app.route('/runes/transfer', methods=['POST'])
def transferRune():
    args = request.get_json()
    runename = args['rune']
    ordaddr = args['OrdinalAddress']
    payaddr = args['PaymentAddress']
    wallet = args['wallet']
    recipient = args['recipient']
    amount = args['amount']
    if wallet == 'xverse':
        pubkey = args['pubKey']
    return requests.post(URL+"/runes/transfer", json=args).json()

@app.route('/runes/pre-mint', methods=['POST'])
def PreMint():
    args = request.get_json()
    rune = args['rune']
    fee = args['feeRate']
    userAddress = args['OrdinalAddress']
    try:
        destination = args['recipient']
    except:
        destination = userAddress
    refundAddress = args['PaymentAddress']
    wallet = args['wallet']
    if wallet=='xverse':
        pubkey = args['pubKey']
    repeats = args['repeats']
    return requests.post(URL+"/runes/pre-mint", json=args).json()

@app.route('/runes/mint', methods=['POST'])
def serverMint():
    args = request.get_json()
    txid = args['txid']
    userAddress = args['OrdinalAddress']
    if pymongo.db.mintorders.find_one({'Payment': txid}):
        return jsonify({'error': 'This txid was already submitted as payment for an order.'})
    return requests.post(URL+"/runes/mint", json=args).json()

@app.route('/runes/mint-orders', methods=['POST'])
def getMintOrders():
    args = request.get_json()
    userAddress = args['OrdinalAddress']
    orders = pymongo.db.mintorders.find({'UserAddress': userAddress})
    if len(orders)>0:
        return jsonify(orders)
    return {}

@app.route('/runes/chart', methods=['POST'])
def runeChart():
    args = request.get_json()
    rune = args['rune']
    data = [a for a in pymongo.db.chart.find({'rune':rune}, {'_id':0})]
    tradeInfo = pymongo.db.tradingInfo.find_one({'Rune':rune}, {'_id':0})
    return jsonify({'chart': data, 'info': tradeInfo})

@app.route('/runes/trading-info', methods=['POST'])
def runeTradeInfo():
    data = [a for a in pymongo.db.tradingInfo.find({}, {'_id':0}).sort('Volume',-1)]
    return jsonify({'info': data[:25]})

@app.route('/runes/total', methods=['POST','GET'])
def getTotal():
    counts = pymongo.db.counts.find_one({})
    total = counts['mints'] + counts['trades'] + counts['transfers']
    return jsonify({'total': total})

@app.route('/runes/create-counteroffer', methods=['POST'])
def counteroffer():
    args = request.get_json()
    payaddr = args['PaymentAddress']
    ordaddr = args['OrdinalAddress']
    wallet = args['wallet']
    price = args['price']
    id = args['id']
    if wallet == 'xverse':
        pubkey = args['pubKey']
    listing = pymongo.db.runelistings.find_one({"_id": ObjectId(id)})
    if (listing == None):
        return jsonify({'error': "That listing does not exist.", 'code':error_offer_not_exist})
    if (listing['valid'] != True):
        return jsonify({'error':"This listing is no longer valid.", 'code': error_offer_is_invalid})
    if price > listing['price']:
        return jsonify({'error': "You are offering to pay more than it is listed for. Just buy normally."})
    return requests.post(URL+"/runes/create-counteroffer", json=args).json()

@app.route('/runes/place-counteroffer', methods=['POST'])
def counterofferPost():
    args = request.get_json()
    ordaddr = args.get('OrdinalAddress')
    payaddr = args.get('PaymentAddress')
    wallet = args.get('wallet')
    price = args['price']
    id = args.get('id')
    pst = args.get('psbt')
    listing = pymongo.db.runelistings.find_one({"_id": ObjectId(id)})
    if (listing == None):
        return jsonify({'error': "That listing does not exist.", 'code':error_offer_not_exist})
    if (listing['valid'] != True):
        return jsonify({'error':"This listing is no longer valid.", 'code':error_offer_is_invalid})
    return requests.post(URL+"/runes/place-counteroffer", json=args).json()

@app.route('/runes/complete-counteroffer', methods=['POST'])
def CompleteCounterOffer():
    args = request.get_json()
    id = args.get('id')
    txid = args.get('txid')
    wallet = args.get('wallet')
    listing = pymongo.db.runelistings.find_one({"_id": ObjectId(id)})
    if (listing == None):
        return jsonify({'error': "That listing does not exist.", 'code':error_offer_not_exist})
    if (listing['valid'] != True):
        return jsonify({'error':"This listing is no longer valid.", 'code':error_offer_is_invalid}) 
    return requests.post(URL+"/runes/complete-counteroffer", json=args).json()

if __name__ == "__main__":
    app.run(debug=True)
