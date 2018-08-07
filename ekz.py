from app import app, db
from app.models import User, Billfold, Transactions, CryptoInfo

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Billfold': Billfold,
        'Transactions': Transactions, 'CryptoInfo': CryptoInfo }
