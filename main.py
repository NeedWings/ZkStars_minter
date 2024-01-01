import json
import random
import time
from time import sleep

from eth_account import Account as ethAccount
from web3 import Web3
from loguru import logger

from config import RPC_LIST, ErrorSleepeng, TaskSleep, mintAmount, NET, ref, advanced_mint_mode

def sleeping_sync(address, error = False):
    if error:
        rand_time = random.randint(ErrorSleepeng[0], ErrorSleepeng[1])
    else:
        rand_time = random.randint(TaskSleep[0], TaskSleep[1])
    logger.info(f'[{address}] sleeping {rand_time} s')
    time.sleep(rand_time)

class Account():
    w3 = {}
    def __init__(self, private_key: str):
        self.private_key = private_key
        self.address = ethAccount.from_key(private_key).address
        self.formatted_hex_address = self.address
        self.setup_w3()

    def setup_w3(self):
        for chain in RPC_LIST:
            self.w3[chain] =  Web3(Web3.HTTPProvider(random.choice(RPC_LIST[chain])))

    def get_w3(self, net_name):
        return self.w3[net_name]
        
    def send_txn(self, txn, net):
        for i in range(10):
            try:
                w3: Web3 = self.w3[net]
                gasEstimate = w3.eth.estimate_gas(txn)
                
                txn['gas'] = round(gasEstimate*1.5) 
                signed_txn = w3.eth.account.sign_transaction(txn, private_key=self.private_key)
                tx_token = w3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))

                logger.success(f"[{self.address}] sending txn: {tx_token}")
                success = self.wait_until_txn_finished(tx_token, net)
                return success, signed_txn, tx_token
            except Exception as e:
                logger.error(f"[{self.address}] got error: {e}")
                sleeping_sync(self.address, True)
        return False, "0x0", "0x0"

    
    def wait_until_txn_finished(self, hash, net, max_time = 500):
        w3 = self.w3[net]
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > max_time:
                    logger.error(f'[{self.address}] {hash} transaction is failed (timeout)')
                    return False
                receipts = w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")

                if status == 1:
                    logger.success(f"[{self.address}] {hash} is completed")
                    return True
                elif status is None:
                    #print(f'[{hash}] still processed') #DEBUG
                    sleep(0.3)
                elif status != 1:
                    logger.error(f'[{self.address}] [{hash}] transaction is failed')
                    return False
            except:
                #print(f"[{hash}] still in progress") #DEBUG
                sleep(1)         


class TxnDataHandler:
      
    def __init__(self, sender, net_name, w3 = None) -> None:
        self.address = sender.address
        self.net_name = net_name
        if w3:
            self.w3 = w3
        else:
            self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_LIST[net_name])))
    
    def get_gas_price(self):
        while True:
            try:
                gas_price = self.w3.eth.gas_price
                return round(gas_price)
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                sleeping_sync(f'[{self.address}] Error fault. Update after ')


    def get_txn_data(self, value=0):
        gas_price = self.get_gas_price()


        data = {
            'chainId': self.w3.eth.chain_id, 
            'nonce': self.w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }


        if self.net_name in ["avalanche", "polygon", "arbitrum", "ethereum", "base", "optimism", "linea"]:
            data["type"] = "0x2"


        if self.net_name not in ['arbitrum', "avalanche", "polygon", "ethereum", "base", "optimism", "linea"]:
            data["gasPrice"] = gas_price

        else:
            data["maxFeePerGas"] = gas_price
            if self.net_name == "polygon":
                data["maxPriorityFeePerGas"] = Web3.to_wei(30, "gwei")
            elif self.net_name == "avalanche" or self.net_name == "base" or self.net_name == "optimism" or self.net_name == "linea":
                data["maxPriorityFeePerGas"] = gas_price
            elif self.net_name == "ethereum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.05, "gwei")
            elif self.net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.01, "gwei")
        
    
        return data

contracts = {
        "zora": """0xdc61E7116bEF1B93E6e6FDF3433aF98DbCb6283f
0x8c6438F4623dF484E9aBbB30513Fe2a8015f4A43
0xa91DABF33dDE0b8AF6Fc1F04cC1963FC93f09aC6
0x71ca33aE91575Bdd0EFC0c68150A4DdA089DfE99
0x5AcaE546De874E184462Ee33645df548880804AD
0xcaCa1262e5658554de0C47C9f12c1f82a1317c9a
0xa4A19D76112558410a98495C038414EcF58aD54e
0xA0a00b6AF66af7060E3eCAcbE2217973965214d1
0x687C6a52ccDCf68CD6C7E30F8eA3A6Af03692b00
0x97FbBC31c721B57e7a70EF67768cd54Ceaa1bF63
0x1Bd5A4996F350c3487Ea2ba6CBa12A9498234740
0xbf7c28d2C5eB893A457cb61055221fC5083045f1
0x7a8a92a5bF3d4daFf9F5e87dBaCaF5f2160DB883
0xa632068ff2Ba03e1720B7F31c107F6B89D41D969
0x8e6644f3525BDe2ed9C064811C6aC728655DFcb1
0x0F93919EEA04fcAE2200141C029Bd162901453f7
0x3A3e56c8C5e0dC6552bDa4F079C881749b35cF00
0x3db72c8f8512416f0193b7a887FAc61a26751249
0xBadd3f2755C0054Aa2bE89d4C51A5D584F4C97B5
0xC35fba7b7001f25a4Db42B30eFDdb5B41e9808ab""".split("\n"),
        "scroll": """0x609c2f307940B8f52190b6D3D3A41C762136884E
0x16c0Baa8a2aA77fab8d0aeCe9B6947EE1b74B943
0xc5471e35533E887f59Df7A31F7C162Eb98F367F7
0xF861f5927C87bC7C4781817b08151d638dE41036
0x954E8AC11c369ef69636239803a36146BF85e61B
0xa576aC0A158EBDCC0445e3465adf50E93dD2CAd8
0x17863384C663c5f95e4e52D3601F2FF1919ac1aA
0x4C2656a6D1c0ecac86f5024e60d4F04DBB3d1623
0x4E86532CEDF07c7946e238bD32Ba141b4ed10c12
0x6b9db0FfCb840C3D9119B4fF00F0795602c96086
0x10D4749Bee6a1576AE5E11227BC7F5031aD351e4
0x373148e566E4c4C14f4eD8334aBa3a0Da645097a
0xDacbAc1C25d63B4B2B8BfDBF21C383e3CCFF2281
0x2394b22B3925342F3216360b7b8F43402E6A150b
0xf34f431E3fC0aD0D2beb914637b39f1ecf46c1Ee
0x6f1E292302DCe99e2A4681bE4370D349850Ac7C2
0xA21faC8b389f1f3717957a6BB7d5Ae658122fc82
0x1b499d45E0Cc5e5198b8A440f2D949F70E207A5D
0xEC9bEF17876D67de1F2EC69F9a0E94De647FcC93
0x5e6c493Da06221fed0259a49bEac09EF750C3De1""".split("\n"),
        "zksync": """0xe7Ed1c47E1e2eA6e9126961df5d41798722A7656
0x53424440d0EaD57e599529B42807a0BA1965dd66
0x406B1195f4916B13513Fea102777DF5bd4AF06Eb
0xd834c621deA708a21B05EAf181115793EaA2f9D9
0xf19b7027d37c3321194d6C5F34Ea2E6cbc73fa25
0x56Bf83E598ce80299962bE937fE0Ba54F5d5E2b2
0xaFec8DF7b10303C3514826C9e2222a16f1486BEe
0x8595D989a96cDBDc1651e3C87ea3D945E0460097
0x945B1eDCd03e1D1Ad9255c2b28e1c22F2C819F0e
0x808D59a747BfEDd9bcb11A63B7E5748D460b614D
0xC92fc3F19645014c392825e3CfA3597412B0D913
0x8Dd8706CBC931c87694E452CAa0a83A564753241
0x8DD3c29F039E932eBd8eaC873b8b7A56d17e36c6
0xCA0848cADb25e6Fcd9c8cE15BcB8f8Da6C1fC519
0x06d52C7E52E9F28e3AD889ab2083fE8Dba735D52
0x86f39D51C06CaC130CA59eABEdC9233A49fCC22a
0xEE0D4A8F649D83F6BA5e5c9E6c4D4F6ae846846A
0xfda7967C56CE80f74B06e14aB9c71c80Cb78b466
0x0d99EFCde08269e2941A5e8A0a02d8e5722403fC
0xf72CF790AC8D93eE823014484fC74F2f1E337Bf6""".split("\n"),
        "linea": """0xdc61E7116bEF1B93E6e6FDF3433aF98DbCb6283f
0x8c6438F4623dF484E9aBbB30513Fe2a8015f4A43
0xa91DABF33dDE0b8AF6Fc1F04cC1963FC93f09aC6
0x71ca33aE91575Bdd0EFC0c68150A4DdA089DfE99
0xB0a56867945D918fc9Cd058Af248a2b54e1f816b
0x5AcaE546De874E184462Ee33645df548880804AD
0xcaCa1262e5658554de0C47C9f12c1f82a1317c9a
0xa4A19D76112558410a98495C038414EcF58aD54e
0xA0a00b6AF66af7060E3eCAcbE2217973965214d1
0x687C6a52ccDCf68CD6C7E30F8eA3A6Af03692b00
0x97FbBC31c721B57e7a70EF67768cd54Ceaa1bF63
0x1Bd5A4996F350c3487Ea2ba6CBa12A9498234740
0xbf7c28d2C5eB893A457cb61055221fC5083045f1
0x7a8a92a5bF3d4daFf9F5e87dBaCaF5f2160DB883
0xa632068ff2Ba03e1720B7F31c107F6B89D41D969
0x8e6644f3525BDe2ed9C064811C6aC728655DFcb1
0x0F93919EEA04fcAE2200141C029Bd162901453f7
0x3A3e56c8C5e0dC6552bDa4F079C881749b35cF00
0x3db72c8f8512416f0193b7a887FAc61a26751249
0xBadd3f2755C0054Aa2bE89d4C51A5D584F4C97B5""".split("\n"),
        "base": """0x657130a14E93731dFEcC772d210AE8333303986c
0x4C78c7D2F423cf07c6DC2542ac000c4788f03657
0x004416bef2544DF0F02F23788C6adA0775868560
0x39B06911D22F4D3191827ED08AE35b84F68843e4
0x8a6a9Ef84CD819A54EEe3cF7CFD351d21Ab6b5FE
0x8fb3225D0A85f2A49714Acd36cDCD96a7B2B7FbC
0x91ad9Ed35B1E9FF6975aa94690fa438EFB5A7160
0x32D8EEB70eAB5f5962190A2bb78A10A5A0958649
0xAB62313752F90c24405287AD8C3bcf4c25c26E57
0x6F562B821b5cb93d4de2B0Bd558cc8E46b632a08
0xb63159A26664A89abce783437fC17786af8bb46d
0x7E6B32D7Eecddb6BE496f232Ab9316a5bf9f4e17
0xCB03866371FB149F3992F8d623D5AAa4B831e2Fd
0x78C85441F53A07329e2380e49f1870199F70cEE1
0x54C49cB80a0679E3217F86d891859B4E477b56C3
0xAd6f16F5fF3461c83d639901BAE1fb2A8A68aA31
0x023A7c97679F2C121A31BaCF37292Dabf7AB97E9
0xd3c6386362daBAb1a30aCC2c377D9AC2cc8B7B16
0x5dabFf127caD8D075b5ceA7f795DCBae1ddf471d
0xeD0407D6B84B2c86418CaC16a347930B222B505C""".split("\n")
}

ABI = [{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"baseURI_","type":"string"},{"internalType":"uint256","name":"ref_precent_","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"name":"ERC721IncorrectOwner","type":"error"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ERC721InsufficientApproval","type":"error"},{"inputs":[{"internalType":"address","name":"approver","type":"address"}],"name":"ERC721InvalidApprover","type":"error"},{"inputs":[{"internalType":"address","name":"operator","type":"address"}],"name":"ERC721InvalidOperator","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"ERC721InvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"receiver","type":"address"}],"name":"ERC721InvalidReceiver","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"ERC721InvalidSender","type":"error"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ERC721NonexistentToken","type":"error"},{"inputs":[],"name":"ReentrancyGuardReentrantCall","type":"error"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"approved","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"operator","type":"address"},{"indexed":False,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":True,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getRefPercent","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"ref","type":"address"}],"name":"safeMint","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newPrice","type":"uint256"}],"name":"setPrice","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"newPercent","type":"uint256"}],"name":"setRefPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"to","type":"address"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]

def is_minted(sender: Account, net: str, contract_address: str):
    while True:
        try:
            w3 = sender.get_w3(net)

            contract = w3.eth.contract(contract_address, abi=ABI)

            bal = contract.functions.balanceOf(sender.address).call()
            return not not bal
        except Exception as e:
            logger.error(f"[{sender.address}] got error: {e}")
            sleeping_sync(sender.address, True)

def simple_mint(sender):
    amount = random.randint(mintAmount[0], mintAmount[1])
    logger.info(f"[{sender.address}] going to mint {amount} ZkStars")
    w3 = sender.get_w3(NET)
    txn_data_handler = TxnDataHandler(sender, NET, w3=w3)
    for _ in range(amount):
        while True:
            try:
                contract = w3.eth.contract(random.choice(contracts[NET]), abi=ABI)
                
                price = contract.functions.getPrice().call()

                txn = contract.functions.safeMint(ref).build_transaction(txn_data_handler.get_txn_data(price))

                sender.send_txn(txn, NET)
                sleeping_sync(sender.address)
                break
            except Exception as e:
                logger.error(f"[{sender.address}] got error: {e}")
                sleeping_sync(sender.address, True)

def advanced_mint(sender):
    amount = random.randint(mintAmount[0], mintAmount[1])
    new_contracts = []
    for address in contracts[NET]:
        if not is_minted(sender, NET, address):
            new_contracts.append(address)

    if len(new_contracts) == 0:
        logger.info(f"[{sender.address}] all minted")
        return
    logger.info(f"[{sender.address}] going to mint {amount} ZkStars")

    w3 = sender.get_w3(NET)
    txn_data_handler = TxnDataHandler(sender, NET, w3=w3)

    for _ in range(amount):
        if len(new_contracts) == 0:
            logger.info(f"[{sender.address}] all minted")
            return
        address = random.choice(new_contracts)
        while True:
            try:
                contract = w3.eth.contract(address, abi=ABI)
                
                price = contract.functions.getPrice().call()

                txn = contract.functions.safeMint(ref).build_transaction(txn_data_handler.get_txn_data(price))

                sender.send_txn(txn, NET)
                sleeping_sync(sender.address)
                break
            except Exception as e:
                logger.error(f"[{sender.address}] got error: {e}")
                sleeping_sync(sender.address, True)

        new_contracts.pop(new_contracts.index(address))


def main():
    with open("privates.txt", "r") as f:
        privates = f.read().split("\n")

    accounts = []

    for key in privates:
        if key == "":
            continue
        accounts.append(Account(key))

    if advanced_mint_mode:
        func = advanced_mint
    else:
        func = simple_mint
    random.shuffle(accounts)
    for account in accounts:
        logger.info(f"[{account.address}] in work now")
        func(account)

if __name__ == "__main__":
    main()