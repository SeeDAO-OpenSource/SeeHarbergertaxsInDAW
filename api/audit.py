class AuditClass():
    def __init__(self) -> None:
        self.audituser = ['0xfF7ca7Fe8FdAF2a602191048E10A4b3B072aA1a0', ]

    def get_user(self):
        return self.audituser

    def verify_audit(self, useraddr):
        userlist = self.get_user()
        if useraddr in userlist:
            return True
        else:
            return False
