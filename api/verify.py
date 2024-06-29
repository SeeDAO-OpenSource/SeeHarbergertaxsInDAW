from web3 import Web3
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
web3 = Web3(Web3.HTTPProvider('https://solana-devnet.g.alchemy.com/v2/RgCOfmKVv0DyHWlw_TtCAk9H0c_9er74'))

# 签名验证
def validate(msg, signature, useraddr):
    mesage= encode_defunct(text="%s"%msg)
    try:
        address = web3.eth.account.recover_message(mesage,signature=HexBytes("%s"%signature))
    except Exception as e:
        print(e)
        return False
    if address == useraddr:
        return True
    else:
        return False

if __name__ == "__main__":
    signature = ''
    useraddr = ''
    msg = """"""

    validate(msg=msg, signature=signature, useraddr=useraddr)