import sure
import unittest

from hpitclient import Tutor

class TestTutor(unittest.TestCase):

    def test_constructor(self):
        """
        Tutor.__init__() Test plan:
            -entity_id and api_key are set to params as strings
        """
        test_entity_id = 1234
        test_api_key = 4567
        test_tutor = Tutor(test_entity_id,test_api_key,None)
        
        test_tutor.entity_id.should.equal(str(test_entity_id))
        test_tutor.api_key.should.equal(str(test_api_key))
        test_tutor.callback.should.equal(None)
    
    


