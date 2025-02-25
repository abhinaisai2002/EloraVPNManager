import datetime
from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src import config
from src.accounts.models import Account, AccountUsedTraffic
from src.accounts.schemas import AccountCreate, AccountModify, AccountUsedTrafficResponse
from src.users.models import User

AccountSortingOptions = Enum('AccountSortingOptions', {
    'expire': Account.expired_at.asc(),
    '-expire': Account.expired_at.desc(),
    'created': Account.created_at.asc(),
    '-created': Account.created_at.desc(),
    'modified': Account.modified_at.asc(),
    '-modified': Account.modified_at.desc(),
    'used-traffic': Account.used_traffic.asc(),
    '-used-traffic': Account.used_traffic.desc(),
    'data-limit': Account.data_limit.asc(),
    '-data-limit': Account.data_limit.desc(),
})


def create_account(db: Session, db_user: User, account: AccountCreate):
    db_account = Account(user_id=db_user.id, uuid=account.uuid, email=account.email,
                         data_limit=account.data_limit,
                         expired_at=account.expired_at,
                         enable=account.enable)

    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def create_account_used_traffic(db: Session, db_account: Account, download: int, upload: int):
    db_account_used_traffic = AccountUsedTraffic(account_id=db_account.id, download=download, upload=upload)

    db.add(db_account_used_traffic)
    db.commit()
    db.refresh(db_account_used_traffic)
    return db_account_used_traffic


def update_account(db: Session, db_account: Account, modify: AccountModify):
    db_account.uuid = modify.uuid
    db_account.email = modify.email
    # db_account.used_traffic = modify.used_traffic
    db_account.data_limit = modify.data_limit
    db_account.expired_at = modify.expired_at
    db_account.modified_at = datetime.datetime.utcnow()

    db_account.enable = modify.enable

    db.commit()
    db.refresh(db_account)

    return db_account


def update_account_used_traffic(db: Session, db_account: Account, used_traffic: int):
    db_account.used_traffic = used_traffic

    db.commit()
    db.refresh(db_account)

    return db_account


def reset_traffic(db: Session, db_account: Account):
    db.query(AccountUsedTraffic).filter(AccountUsedTraffic.account_id == db_account.id).delete()
    db_account.used_traffic = 0
    db_account.modified_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(db_account)

    return db_account


def update_account_status(db: Session, db_account: Account, enable: bool = True):
    db_account.enable = enable
    db_account.modified_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(db_account)

    return db_account


def get_accounts(db: Session,
                 offset: Optional[int] = None,
                 limit: Optional[int] = None,
                 sort: Optional[List[AccountSortingOptions]] = None,
                 return_with_count: bool = True,
                 ) -> Tuple[List[Account], int]:
    query = db.query(Account)

    if sort:
        query = query.order_by(*(opt.value for opt in sort))

    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)

    count = query.count()

    if return_with_count:
        return query.all(), count
    else:
        return query.all()


def get_user_last_test_account(db: Session,
                           db_user: User,
                           return_with_count: bool = True
                           ) -> Account:
    query = db.query(Account)

    query = query.order_by(Account.created_at.desc())

    query = query.filter(Account.email.ilike(f"{config.TEST_ACCOUNT_EMAIL_PREFIX}%"))

    return query.first()


def get_account_used_traffic(db: Session,
                             db_account: Account,
                             delta: int = 3
                             ) -> AccountUsedTraffic:
    today = datetime.datetime.now()
    n_days_ago = today - datetime.timedelta(days=delta)

    print('Generate report from ' + str(n_days_ago))

    query = db.query(func.sum(AccountUsedTraffic.download).label("total_download"),
                     func.sum(AccountUsedTraffic.upload).label("total_upload")).filter(
        and_(AccountUsedTraffic.created_at >= n_days_ago, AccountUsedTraffic.account_id == db_account.id)
    )

    sum_result = query.one()

    if query:
        return AccountUsedTrafficResponse(account_id=db_account.id, download=sum_result[0], upload=sum_result[1])

    else:
        return AccountUsedTrafficResponse(account_id=db_account.id)


def get_all_accounts_used_traffic(db: Session,
                                  delta: int = 3
                                  ) -> AccountUsedTraffic:
    today = datetime.datetime.now()
    n_days_ago = today - datetime.timedelta(days=delta)

    print('Generate report from ' + str(n_days_ago))

    query = db.query(func.sum(AccountUsedTraffic.download).label("total_download"),
                     func.sum(AccountUsedTraffic.upload).label("total_upload")).filter(
        and_(AccountUsedTraffic.created_at >= n_days_ago)
    )

    sum_result = query.one()

    if query:
        return AccountUsedTrafficResponse(account_id=0, download=sum_result[0], upload=sum_result[1])

    else:
        return AccountUsedTrafficResponse(account_id=0)


def remove_account(db: Session, db_account: Account):
    db.delete(db_account)
    db.commit()
    return db_account


def get_account(db: Session, account_id: int):
    return db.query(Account).filter(Account.id == account_id).first()
