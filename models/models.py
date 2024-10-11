from peewee_aio import Manager, AIOModel, fields

manager = Manager('aiosqlite:///db.sqlite')


@manager.register
class User(AIOModel):
    id = fields.AutoField()
    tgid = fields.IntegerField()
    username = fields.CharField(default="")
    balance = fields.IntegerField(default=0)
    banstatus = fields.BooleanField(default=False)
    subuntil = fields.DateTimeField(default=0)
    prosubuntil = fields.DateTimeField(default=0)


@manager.register
class Purchase(AIOModel):
    id = fields.AutoField()
    type = fields.CharField()
    sum = fields.IntegerField()
    date = fields.DateTimeField()
    user_id = fields.IntegerField()


@manager.register
class Build(AIOModel):
    id = fields.AutoField()
    tgid = fields.BigIntegerField()
    build_id = fields.CharField()