from mongoengine import Document, StringField, DateTimeField, IntField, FloatField, BooleanField, ListField, EmbeddedDocument, EmbeddedDocumentField

class CounterOffer(EmbeddedDocument):
    OrdinalAddress = StringField()
    PaymentAddress = StringField()
    wallet = StringField()
    price = FloatField()
    psbt = StringField()

class RuneListing(Document):
    PaymentAddress = StringField()
    OrdinalAddress = StringField()
    rune = StringField()
    amount = IntField()
    price = IntField()
    type = StringField()
    psbt = StringField()
    wallet = StringField()
    valid = BooleanField()
    symbol = StringField()
    Created = DateTimeField()
    CounterOffers = ListField(EmbeddedDocumentField(CounterOffer))
    Completed = DateTimeField()

    meta = {'collection': 'runelistings'}
