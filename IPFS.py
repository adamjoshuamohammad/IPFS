import hashlib
import json
import os
import sys
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes=set()
        #Genesis Block
        self.new_block(cid='1', proof=100)

    def register_node(self, address):
        '''
        Add a new node to the list of nodes
        :param address: <str> Address of node
        :return: None
        '''

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        '''
        Verifies the CID of each block to check
        if blockchain is valid.
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        '''

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            #Check that the CID of the block is correct
            if block['cid'] != self.generate_cid(last_block):
                return False
            
            #Check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        
        return True

    def resolve_conflicts(self):
        '''
        Consensus Algorithm: replaces chain with the longest one in the network
        :return: <bool> True if chain was replaced, False if not replaced
        '''

        neighbors = self.nodes
        new_chain = None

        #We're only looking for chains longer than ours
        max_length = len(self.chain)

        #Grab and verify the chains from all the nodes in our network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                #Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain


        if new_chain:
            self.chain = new_chain
            return True
        
        return False
    
    def new_block(self, proof, cid):
        '''
        Create a new block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param CID: (Optional) <str> Previous CID
        :return: <dict> New Block
        '''

        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'cid': cid or self.generate_cid(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, isbn):
        '''
        Creates a new transaction to go into the next mined Block
        :param from: <str> Address of the Sender
        :param to: <str> Address of the Recipient
        :return: <int> The index of the Block that will hold this transaction
        '''
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
        })

        return self.last_block['index']+1

    @staticmethod
    def generate_cid(block):
        '''
        Creates a SHA-256 hash of a Block to represent CID
        :param block: <dict> Block
        :return: <str>
        '''
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #returns the last block in the chain
        return self.chain[-1]

    def new_transaction(self, sender, recipient, isbn):
        '''
        Creates a new transaction to fo into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param isbn: <int> ISBN of book
        :return: <int> The index of the Block that will hold this transaction
        '''

        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
        })

        return self.last_block['index']+1


    def proof_of_work(self, last_block):
        '''
        Simple Proof of Work Algorithm:
        - Find a number p' such that generate_cid(pp) contains 4 leading zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        '''

        last_proof = last_block['proof']
        last_cid = self.generate_cid(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_cid) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_cid):
        '''
        Validates the Proof: Does generate_cid(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        '''

        guess = f'{last_proof}{proof}{last_cid}'.encode()
        guess_cid = hashlib.sha256(guess).hexdigest()
        return guess_cid[:4]=="0000"

#Instantiating the Blockchain
# Significant portions taken from geeksforgeeks.com
# URL:https://www.geeksforgeeks.org/python-program-to-merge-two-files-into-a-third-file/

# must be in directory with node.cpp executable

argc = len(sys.argv)
blocks = []
i = 1

while i < argc:
    blocks.append(argv[i])
    i += 1

os.system('./node 54000') # init user node (collects data)
for block in blocks:
    os.system('./node 54001 54000 move '+block) # collect each block

filename = input('Enter desired filename: ')
with open(filename, 'w') as outfile:
    for b in blocks:
        with open (b+'.txt') as infile:
            outfile.write(infile.read())
        outfile.write('\n')