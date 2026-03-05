import uuid


def generate_btc_address():

    address = "btc_" + str(uuid.uuid4())

    return address