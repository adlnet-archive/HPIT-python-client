import sure
import unittest
import httpretty
import json
import pytest
from mock import *

from hpitclient import Tutor
from hpitclient.exceptions import InvalidMessageNameException
from hpitclient.exceptions import ResponseDispatchError
from hpitclient.exceptions import InvalidParametersError

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
    
    @httpretty.activate
    def test_send_blocking(self):
        """
        Tutor.send_blocking() Test plan:
            - if message is transaction, then it should raise an exception
            - make a mock endpoint, return a message id
            - test a timeout
                - mock poll_responses to return empty dict, should return none
            - test a valid response
                - mock poll_responses to return a valid response with desired message ID
        """
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/message",
                            body='{"message_id":"4"}',
                            )
        
        subject = Tutor(123,456,None)
 
        subject.poll_wait = -1
        subject.send_log_entry = MagicMock()
        
        #transaction should return a exception
        subject.send_blocking.when.called_with("transaction", {"payload":"something"}).should.throw(InvalidMessageNameException)
        
        #this should timeout
        subject.block_timeout_time = 0
        subject._poll_responses = MagicMock(return_value = [])
        subject.send_blocking("message_name",{"payload":"something"}).should.equal(None)

        #this should work
        subject.block_timeout_time = 999999
        subject._poll_responses = MagicMock(return_value = [{"message":{"message_id":"4"},"response":{"data":"1"}}])
        subject.send_blocking("message_name",{"payload":"something"}).should.equal({"data":"1"})
        

