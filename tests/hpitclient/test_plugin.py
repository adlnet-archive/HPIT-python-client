import sure
import unittest
import httpretty

from hpitclient import Plugin
from hpitclient.exceptions import PluginPollError, BadCallbackException, InvalidParametersError

import json
import shlex
from unittest.mock import MagicMock

from datetime import datetime

class TestPlugin(unittest.TestCase):

    def setUp(self):
        self.test_entity_id = 1234
        self.test_api_key = 4567

        self.test_plugin = Plugin(self.test_entity_id,self.test_api_key,None)

    def tearDown(self):
        self.test_plugin = None

    @httpretty.activate
    def test_constructor(self):
        """
        Plugin.__init__() Test plan:
            -ensure connected is false
            -ensure name is argument
            -entity id and api key are strings
        """
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
        
        self.test_plugin.connected.should.equal(False)
        self.test_plugin.entity_id.should.equal(str(self.test_entity_id))
        self.test_plugin.api_key.should.equal(str(self.test_api_key))
        

    @httpretty.activate
    def test_register_transaction_callback(self):
        """
        Plugin.register_transaction_callback() Test plan:
            -check if transaction_callback = param
            -make sure callback is callable
        """
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
       
        def simple_callback():
            pass
        
        self.test_plugin.register_transaction_callback.when.called_with(4).should.throw(BadCallbackException)
        self.test_plugin.register_transaction_callback(simple_callback)
        self.test_plugin.transaction_callback.should.equal(simple_callback)


    @httpretty.activate
    def test_clear_transaction_callback(self):
        """
        Plugin.clear_transaction_callback() Test plan:
            - make sure self.transaction_callback is None
        """
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/unsubscribe",
                                body='',
                                )
        
        def simple_callback():
            pass

        self.test_plugin.transaction_callback = simple_callback
        self.test_plugin.clear_transaction_callback()
        self.test_plugin.transaction_callback.should.equal(None)
        
        
    @httpretty.activate
    def test_list_subscriptions(self):
        """
        Plugin.list_subscriptions() Test plan:
            -ensure the subscriptions are in return value
            -ensure that 'unknown' subscriptions set callback to none
            -ensure that 'known' subsriptsion still have their callbacks set
            -ensure that the return value is a dictionary
        """
        httpretty.register_uri(httpretty.GET,"https://www.hpit-project.org/plugin/subscription/list",
                                body='{"subscriptions":["subscription1","subscription2"]}',
                                )
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
        
        self.test_plugin.callbacks["subscription1"] = 4
        
        subscriptions = self.test_plugin.list_subscriptions()
        
        "subscription1".should.be.within(subscriptions)
        "subscription2".should.be.within(subscriptions)
        
        self.test_plugin.callbacks["subscription1"].should.equal(4)
        self.test_plugin.callbacks["subscription2"].should.equal(None)
        
        subscriptions.should.be.a('dict')
        
        
       
    @httpretty.activate
    def test_subscribe(self):
        """
        Plugin.subscribe() Test plan:
            -ensure that args passed are then in callbacks dict 
        """
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='OK',
                                )
        
        def test_callback():
            pass
        
        self.test_plugin = Plugin("test_name",None)
        
        self.test_plugin.subscribe({'test_event': test_callback})
        self.test_plugin.callbacks["test_event"].should.equal(test_callback)
        

    @httpretty.activate
    def test_unsubscribe(self):
        """
        Plugin.unsubscribe() Test plan:
            -ensure that called numerous times for args
            -ensure event name is removed from callbacks
            -if not in callbacks, make sure keyerror not raised
        """
       
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/unsubscribe",
                                body='OK',
                                )
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
        
        self.test_plugin = Plugin("test_name",None)
            
        def test_callback(self):
            pass
        
        self.test_plugin.callbacks["test_event2"] = test_callback

        self.test_plugin.unsubscribe("test_event","test_event2")
        
        self.test_plugin.callbacks.should_not.have.key("test_event")
        self.test_plugin.callbacks.should_not.have.key("test_event2")
        
        
    @httpretty.activate
    def test_poll(self):
        """
        Plugin._poll() Test plan:
            -ensure we get something from server
        """
        
        httpretty.register_uri(httpretty.GET,"https://www.hpit-project.org/plugin/message/list",
                                body='{"messages":"4"}',
                                )
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
        
        self.test_plugin = Plugin("test_name",None)
        self.test_plugin._poll().should_not.equal(None)
        

    def test_handle_transactions(self):
        """
        Plugin._handle_transactions() Test plan:
            - 
        """
        
        time = datetime.now()
        event_param = {"transactions": [
                    {"message_id": '1234', "sender_entity_id": '4567', "message_name":"test_event","time_created":time,"message":{"thing": "test message"}},
                    {"message_id": '1234', "sender_entity_id": '4567', "message_name":"test_event","time_created":time,"message":{"thing": "test message"}},
        ]}
        self.test_plugin._get_data=MagicMock(return_value=event_param)
        
        self.test_plugin.transaction_callback= MagicMock()
        
        self.test_plugin._handle_transactions().should.equal(True)
        self.test_plugin.transaction_callback.assert_called_with(event_param["transactions"][0]["message"])
        self.test_plugin.transaction_callback.call_count.should.equal(2)

    wildCardCalled = False
    @httpretty.activate
    def test_dispatch(self):
        """
        Plugin._dispatch() Test plan:
            -if pre_dispatch hook not defined or false, return false
            -if post_dispatch hook not defined or false, return false
            -ensure pluginpollerror raised if wildcard callback not set on key error
            -ensure wildcard callback is called if callback not set on key error if exists
            -ensure pluginpollerror raised if no callback set
            -ensure typerror raised if its not a function
            -true on success
            
            Table:
            pre_dispatch   post dispatch    callback[event]=    wildcard set  callback callable     result            
            
            returnFalse    *                set                 *             *                     false
            returnTrue     returnFalse      set                 *             Yes                   false
            returnTrue     returnTrue       not set             Not callable  *                     PluginPollError
            returnTrue     returntrue       not set             Yes           *                     callbackCalled = True, rv True
            returnTrue     returnTrue       None                *             No (none)             PluginPollError
            returnTrue     returnTrue       4                   *             No (4)                TypeError
            returnTrue     returnTrue       set                 *             Yes                   true
        """
        
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
        
        def returnTrue():
            return True
        def returnFalse():
            return False
        def testCallback(param):
            pass
        def wildCard(param):
            global wildCardCalled
            wildCardCalled = True
            
        time=datetime.now()
        event_param = [{"message_id": '1234', "sender_entity_id": '4567', "message_name":"test_event","time_created":time,"message":{"thing": "test message"}}]
        
        setattr(self.test_plugin,"pre_dispatch_messages",returnFalse)
        self.test_plugin._dispatch(event_param).should.equal(False)
        
        setattr(self.test_plugin,"pre_dispatch_messages",returnTrue)
        setattr(self.test_plugin,"post_dispatch_messages",returnFalse)
        self.test_plugin.callbacks["test_event"] = testCallback
        self.test_plugin._dispatch(event_param).should.equal(False)
        
        del self.test_plugin.callbacks["test_event"]
        self.test_plugin.wildcard_callback = 4
        self.test_plugin._dispatch.when.called_with(event_param).should.throw(PluginPollError)
        
        setattr(self.test_plugin,"post_dispatch_messages",returnTrue)
        self.test_plugin.wildcard_callback = wildCard
        self.test_plugin._dispatch(event_param).should.equal(True)
        wildCardCalled.should.equal(True)
        
        self.test_plugin.callbacks["test_event"] = None
        self.test_plugin._dispatch.when.called_with(event_param).should.throw(PluginPollError)
        
        self.test_plugin.callbacks["test_event"] = 4
        self.test_plugin._dispatch.when.called_with(event_param).should.throw(TypeError)
        
        self.test_plugin.callbacks["test_event"] = testCallback
        self.test_plugin._dispatch(event_param).should.equal(True)
        

    @httpretty.activate
    def test_send_reponse(self):
        """
        Plugin.send_response() Test plan:
            -make sure no exception raised
        """
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/response",
                                body='OK',
                                )
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/plugin/subscribe",
                                body='',
                                )
        
        self.test_plugin = Plugin("test_name",None)
        self.test_plugin.send_response(4,{"payload":"4"})


    @httpretty.activate
    def test_share_message(self):
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/share-message",
            body='OK',
        )

        self.test_plugin.share_message.when.called_with(None, None).should.throw(InvalidParametersError)
        self.test_plugin.share_message.when.called_with('', None).should.throw(InvalidParametersError)
        self.test_plugin.share_message.when.called_with([], None).should.throw(InvalidParametersError)
        self.test_plugin.share_message.when.called_with({}, None).should.throw(InvalidParametersError)
        self.test_plugin.share_message.when.called_with('thing', None).should.throw(InvalidParametersError)
        self.test_plugin.share_message.when.called_with('thing', '').should.throw(InvalidParametersError)
        self.test_plugin.share_message.when.called_with('thing', []).should.throw(InvalidParametersError)
        self.test_plugin.share_message('thing', '4').should.equal(True)
        self.test_plugin.share_message('thing', ['4', '5', '6']).should.equal(True)


    @httpretty.activate
    def test_secure_resource(self):
        httpretty.register_uri(httpretty.POST,"https://www.hpit-project.org/new-resource",
            body='{"resource_id":"1234"}',
            content_type="application/json"
        )

        self.test_plugin.secure_resource.when.called_with(None).should.throw(InvalidParametersError)
        self.test_plugin.secure_resource.when.called_with('').should.throw(InvalidParametersError)
        self.test_plugin.secure_resource.when.called_with([]).should.throw(InvalidParametersError)
        self.test_plugin.secure_resource.when.called_with({}).should.throw(InvalidParametersError)
        self.test_plugin.secure_resource('4').should.equal('1234')

    def test_get_shared_messages(self):
        self.test_plugin.get_shared_messages(None).should.equal(None)
        json_string = json.dumps({
                "shared_messages": {
                    "message_name": ["id1","id2","id3"],
                    "message_name2":"id4",
                }
            })
        json_string = shlex.quote(json_string)
        
        self.test_plugin.get_shared_messages(json_string).should.equal({
                "message_name": ["id1","id2","id3"],
                "message_name2":"id4",
            })
        
        json_string = json.dumps({
                "shared_messages": {
                    "message_name": 4,
                    "message_name2":"id4",
                }
            })
        json_string = shlex.quote(json_string)
        self.test_plugin.get_shared_messages(None).should.equal(None)
        
        json_string = json.dumps({
                "wrong key": {
                    "message_name": 4,
                    "message_name2":"id4",
                }
            })
        json_string = shlex.quote(json_string)
        self.test_plugin.get_shared_messages(None).should.equal(None)
        
        json_string = json.dumps({
                "wrong key": {
                    "5": "id2",
                    "message_name2":"id4",
                }
            })
        json_string = shlex.quote(json_string)
        self.test_plugin.get_shared_messages(None).should.equal(None)
