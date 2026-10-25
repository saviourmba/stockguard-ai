import pytest
from stockguard_core import connect,start,submit,recount,investigate,expected

@pytest.fixture
def db():
    d=connect(':memory:')
    yield d
    d.close()

def test_blind_count_and_shortage(db):
    a=start(db,'AMOX500')
    assert 'expected' not in a
    first=submit(db,a['audit_id'],68)
    assert (first['expected'],first['shortage'],first['estimated_retail_exposure_naira'])==(75,7,10500)
    assert first['status']=='awaiting_recount'
    again=recount(db,a['audit_id'],68)
    assert again['status']=='discrepancy_confirmed'
    case=investigate(db,a['audit_id'])
    assert case['investigation']['shortage']==7
    assert case['notification']['status']=='queued_for_review'
    assert investigate(db,a['audit_id'])['duplicate_prevented'] is True

def test_recount_resolution(db):
    a=start(db,'INHALER')
    assert submit(db,a['audit_id'],25)['status']=='awaiting_recount'
    assert recount(db,a['audit_id'],28)['status']=='resolved_on_recount'
    with pytest.raises(ValueError): investigate(db,a['audit_id'])

def test_invalid_and_duplicate(db):
    a=start(db,'VITC')
    with pytest.raises(ValueError): submit(db,a['audit_id'],-1)
    assert submit(db,a['audit_id'],20)['status']=='matched'
    with pytest.raises(ValueError): submit(db,a['audit_id'],20)
    with pytest.raises(ValueError): investigate(db,a['audit_id'])
