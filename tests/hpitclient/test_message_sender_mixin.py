import sure
import httpretty
import json
import pytest
from mock import *

from hpitclient.message_sender_mixin import MessageSenderMixin
from hpitclient.exceptions import InvalidMessageNameException
from hpitclient.exceptions import ResponseDispatchError
from hpitclient.exceptions import InvalidParametersError

def send_callback():
    print("test callback")

@httpretty.activate
def test_send():
    """
    MessageSenderMixin._send() Test plan:
        -ensure events named transaction raise error
        -ensure callback is set on success
        -ensure that a response is received
    """
    
    test_payload = {"item":"shoe"}
    
    httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/message",
                            body='{"message_id":"4"}',
                            )
    
    subject = MessageSenderMixin()
    
    subject.send.when.called_with("transaction",test_payload,None).should.throw(InvalidMessageNameException)
    
    response = subject.send("test_event",test_payload,send_callback)
    subject.response_callbacks["4"].should.equal(globals()["send_callback"])
    
    response.should.equal({"message_id":"4"})
    
@httpretty.activate
def test_send_transaction():
    """
    MessageSenderMixin._send_transaction() Test plan:
        -ensure callback is set on success
        -ensure that a response is received
    """
    
    test_payload = {"item":"shoe"}
    
    httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/message",
                            body='{"message_id":"4"}',
                            )
    
    subject = MessageSenderMixin()
    
    response = subject.send("test_event",test_payload,send_callback)
    subject.response_callbacks["4"].should.equal(globals()["send_callback"])
    
    response.should.equal({"message_id":"4"})
    
@httpretty.activate
def test_poll_responses():
    """
    MessageSenderMixin._poll_responses() Test plan:
        -Ensure False returned if pre_poll_responses hook returns false
        -Ensure False returned if post_poll_responses hook returns false
        -Ensure a collection of responses returned on success
    """
    
    httpretty.register_uri(httpretty.GET,"https://www.hpit-project.org/response/list",
                            body='{"responses":"4"}',
                            )
    
    
    def returnFalse():
        return False
    def returnTrue():
        return True
    
    test_message_sender_mixin = MessageSenderMixin()
    
    setattr(test_message_sender_mixin,"pre_poll_responses",returnFalse)
    setattr(test_message_sender_mixin,"post_poll_responses",returnTrue)
    test_message_sender_mixin._poll_responses().should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_poll_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_poll_responses",returnFalse)
    test_message_sender_mixin._poll_responses().should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_poll_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_poll_responses",returnTrue)
    test_message_sender_mixin._poll_responses().should.equal("4")

def test_dispatch_responses():
    """
    MessageSenderMixin._dispatch_responses() Test plan:
        -Ensure False returned if pre_dispatch_responses hook returns false
        -Ensure False returned if post_dispatch_responses hook returns false
        -Catch invalid response from hpit on [message][id]
        -Catch invaled response from hpit on [response]
        -Catch no callback exception
        -Catch not callable error
        -Ensure true returned on completions
     """

    bad_response = [{"bad_response": "boo"}]
    bad_response2 = [{"message":{"message_id":"4"}}]
    good_response = [{"message": {"message_id":"4"},"response":"2"}]

    
    def returnFalse():
        return False
    def returnTrue():
        return True
    def callback1(payload):
        return True
    
    test_message_sender_mixin = MessageSenderMixin()
    test_message_sender_mixin.send_log_entry = MagicMock()
    
    test_message_sender_mixin.response_callbacks["4"] = callback1
    setattr(test_message_sender_mixin,"pre_dispatch_responses",returnFalse)
    setattr(test_message_sender_mixin,"post_dispatch_responses",returnTrue)
    test_message_sender_mixin._dispatch_responses(good_response).should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_dispatch_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_dispatch_responses",returnFalse)
    test_message_sender_mixin._dispatch_responses(good_response).should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_dispatch_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_dispatch_responses",returnTrue)
   
    test_message_sender_mixin._dispatch_responses(bad_response)
    test_message_sender_mixin.send_log_entry.assert_called_once_with('Invalid response from HPIT. No message id supplied in response.')

    test_message_sender_mixin.send_log_entry.reset_mock()
    test_message_sender_mixin._dispatch_responses(bad_response2)
    test_message_sender_mixin.send_log_entry.assert_called_once_with('Invalid response from HPIT. No response payload supplied.')
    
    del test_message_sender_mixin.response_callbacks["4"]
    test_message_sender_mixin.send_log_entry.reset_mock()
    test_message_sender_mixin._dispatch_responses(good_response)
    test_message_sender_mixin.send_log_entry.assert_called_once_with('No callback registered for message id: 4')

    test_message_sender_mixin.response_callbacks["4"] = 5
    test_message_sender_mixin.send_log_entry.reset_mock()
    test_message_sender_mixin._dispatch_responses(good_response)
    test_message_sender_mixin.send_log_entry.assert_called_once_with("Callback registered for transcation id: 4 is not a callable.")
    
    test_message_sender_mixin.response_callbacks["4"] = callback1
    test_message_sender_mixin._dispatch_responses(good_response).should.equal(True)
    
@httpretty.activate 
def test_get_message_owner():

    subject = MessageSenderMixin()
    subject.send_log_entry = MagicMock()

    httpretty.register_uri(httpretty.GET,
        "https://www.hpit-project.org/message-owner/thing",
        body='{"owner":"4"}',
        content_type="application/json"
    )

    subject.get_message_owner.when.called_with(None).should.throw(InvalidParametersError)
    subject.get_message_owner.when.called_with([]).should.throw(InvalidParametersError)
    subject.get_message_owner.when.called_with({}).should.throw(InvalidParametersError)
    subject.get_message_owner.when.called_with("").should.throw(InvalidParametersError)
    subject.get_message_owner.when.called_with(['thing']).should.throw(InvalidParametersError)
    subject.get_message_owner.when.called_with({'thing': 1}).should.throw(InvalidParametersError)
    subject.get_message_owner('thing').should.equal('4')


@httpretty.activate
def test_share_resource():
    subject = MessageSenderMixin()
    subject.send_log_entry = MagicMock()

    httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/share-resource",
        body='OK',
    )

    subject.share_resource.when.called_with(None, None).should.throw(InvalidParametersError)
    subject.share_resource.when.called_with('', None).should.throw(InvalidParametersError)
    subject.share_resource.when.called_with([], None).should.throw(InvalidParametersError)
    subject.share_resource.when.called_with({}, None).should.throw(InvalidParametersError)
    subject.share_resource.when.called_with('thing', None).should.throw(InvalidParametersError)
    subject.share_resource.when.called_with('thing', '').should.throw(InvalidParametersError)
    subject.share_resource.when.called_with('thing', []).should.throw(InvalidParametersError)
    subject.share_resource('thing', '4').should.equal(True)
    subject.share_resource('thing', ['4', '5', '6']).should.equal(True)
