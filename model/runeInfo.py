from mongoengine import Document, StringField, DateTimeField, IntField, FloatField, BooleanField

class Rune(Document):
    SpacedRune = StringField(required=True, db_field="SpacedRune")
    Created = DateTimeField(db_field="Created")
    Divisibility = IntField(db_field="Divisibility")
    EtchTx = StringField(db_field="EtchTx")
    LimitPerMint = IntField(db_field="LimitPerMint")
    MaxMintNumber = IntField(db_field="MaxMintNumber")
    MintEndAfter = DateTimeField(db_field="MintEndAfter")
    MintEndBlock = IntField(db_field="MintEndBlock")
    MintStartBlock = IntField(db_field="MintStartBlock")
    Minted = IntField(db_field="Minted")
    Premine = IntField(db_field="Premine")
    Progress = FloatField(db_field="Progress")
    RuneID = StringField(db_field="RuneID")
    Supply = IntField(db_field="Supply")
    Symbol = StringField(db_field="Symbol")
    Mintable = BooleanField(db_field="Mintable")

    meta = {'collection': 'runeInfo'}
