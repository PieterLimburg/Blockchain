import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# PART 1 ----------------------------------------------------------
# Building the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, prevHash = '0')
        self.nodes = set()

    def create_block(self, proof, prevHash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prevHash': prevHash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prevProof):
        start = datetime.datetime.now()
        newProof = 1
        checkProof = False
        while checkProof == False:
            hashOperation = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
                end = datetime.datetime.now()
                print('SUCCESS! This is the correct Hash Operation: ' + hashOperation)
                print('Time elapsed: ' + str((end.microsecond - start.microsecond)/1000) + ' ms')
            else:
                newProof +=1
        return newProof

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()

    def is_chain_valid(self, chain):
        prevBlock = chain[0]
        blockIndex = 1
        isValid = True
        while blockIndex < len(chain):
            block = chain[blockIndex]
            print('CHECKING BLOCK ' + str(block['index']))
            if block['prevHash'] != self.hash(prevBlock):
                isValid = False
                return False
            prevProof = prevBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                isValid = False
                return False
            prevBlock = block
            blockIndex += 1
            if isValid == True:
                print('VALID!')
            else:
                print('ERROR!')
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
        'sender': sender,
        'receiver': receiver,
        'amount': amount})
        prevBlock = self.get_prev_block()
        return prevBlock['index'] + 1

    def add_node(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    def replace_chain(self):
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.is_chain_valid(chain):
                    maxLength = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        else:
            return False

# Create the Blockchain
blockchain = Blockchain()

# Create the web app
app = Flask(__name__)

# Create a NODE address
nodeAddress = str(uuid4()).replace('-', '')

# PART 2 ----------------------------------------------------------
# Mining the blockchain
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prevBlock = blockchain.get_prev_block()
    prevProof = prevBlock['proof']
    proof = blockchain.proof_of_work(prevProof)
    prevHash = blockchain.hash(prevBlock)
    blockchain.add_transaction(sender = nodeAddress, receiver = 'TBD', amount = 12)
    block = blockchain.create_block(proof, prevHash)
    response = {'message': 'CONGRATS, BLOCK SUCCESSFULLY MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prevHash': block['prevHash'],
                'transactions': block['transactions']}
    return jsonify(response), 200
    print(proof)

# Get the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    isValid = blockchain.is_chain_valid(blockchain.chain)
    if isValid:
        response = {'message': 'BLOCKCHAIN IS VALID'}
    else:
        response = {'message': 'WARNING!! BLOCKCHAIN IS CORRUPTED'}
    return jsonify(response), 200

# Adding a transaction to the blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transactionKeys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transactionKeys):
        return 'ERROR: MISSING KEY IN TRANSACTIONS', 400
    else:
        index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
        response = {'message': f'SUCCESS! This transaction will be added to Block {index}'}
        return jsonify(response), 201

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes == None:
        return 'ERROR: NO NODES FOUND', 400
    else:
        for node in nodes:
            blockchain.add_node(node)
        response = {
            'message': 'SUCCESS! ALL NODES CONNECTED. LIST OF NODES: ',
            'total nodes': list(blockchain.nodes)}
        return jsonify(response), 201

# Replacing the chain by the longest chain, if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    isChainReplaced = blockchain.replace_chain()
    if isChainReplaced:
        response = {'message': 'CHAIN UPDATED AND REPLACED', 'newChain': blockchain.chain}
    else:
        response = {'message': 'NO CHANGES, CHAIN IS THE LARGEST ALREADY', 'actualChain': blockchain.chain}
    return jsonify(response), 200

# PART 3 ----------------------------------------------------------
# Decentralizing the blockchain


# Run the app
app.run(host = '0.0.0.0', port = 5003)
