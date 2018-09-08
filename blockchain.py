import datetime
import hashlib
import json
from flask import Flask, jsonify

# Building the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, prevHash = '0')

    def create_block(self, proof, prevHash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'prevHash': prevHash}
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prevProof):
        newProof = 1
        checkProof = False
        while checkProof == False:
            hashOperation = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
                print('SUCCESS! This is the correct Hash Operation: ' + hashOperation)
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

# Create the Blockchain
blockchain = Blockchain()

# Create the web app
app = Flask(__name__)

# Mining the blockchain
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prevBlock = blockchain.get_prev_block()
    prevProof = prevBlock['proof']
    proof = blockchain.proof_of_work(prevProof)
    prevHash = blockchain.hash(prevBlock)
    block = blockchain.create_block(proof, prevHash)
    response = {'message': 'CONGRATS, BLOCK SUCCESSFULLY MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prevHash': block['prevHash']}
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

# Run the app
app.run(host = '0.0.0.0', port = 5000)
