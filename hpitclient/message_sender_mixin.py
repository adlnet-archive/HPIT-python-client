from .requests_mixin import RequestsMixin
from .exceptions import ResponseDispatchError
from .exceptions import InvalidMessageNameException
from .exceptions import AuthenticationError, InvalidParametersError, AuthorizationError, ResourceNotFoundError

class MessageSenderMixin(RequestsMixin):
    def __init__(self):
        super().__init__()
        self.response_callbacks = {}
        
        self._add_hooks('pre_poll_responses', 'post_poll_responses', 'pre_dispatch_responses', 'post_dispatch_responses')

    def send(self, message_name, payload, callback=None):
        """
        Sends a message to the HPIT server. Messages are the meat of how
        HPIT works. All messages are asyncronous and non-blocking. Responses
        are not guarenteed to be prompt due to the distributed nature of HPIT. However,
        it is our goal to ensure response times are as minimal as possible. Responses times
        are dependendent on the network, HPIT server load, and the networking and processing
        constraints of the plugins.

        Each message consists of two main things:
            - message_name: string - The name of the message we are sending to HPIT. This will determine
            which plugins recieves the message.
            - payload: dict - A Python dictionary of the data to send to HPIT and to whatever plugins
            are listening to and will process the message. The dictionary will be converted to JSON in
            route to HPIT.

        Optionally you can pass a callback, and as this message sender polls HPIT for responses
        !!!IF!!! it recieved such a response from a plugin your callback will be called to handle
        the response with any information from the plugin.

        Returns: requests.Response : class - A request.Response object returned from submission 
        of the message. This is not the eventual response from HPIT. It is simply an acknowledgement
        the data was recieved. You must send in a callback to handle the actual HPIT response.
        """
        
        if message_name == "transaction":
            raise InvalidMessageNameException("Cannot use message_name 'transaction'.  Use send_transaction() method for datashop transactions.")
            
        response = self._post_data('message', {
            'name': message_name,
            'payload': payload
        }).json()

        if callback:
            self.response_callbacks[response['message_id']] = callback

        return response
        
    def send_transaction(self, payload, callback= None):
        """
        This method functions identially as send, but inserts "transaction" as the message.
        This is specifically for DataShop transactions.
        See send() method for more details.
        """
        
        response = self._post_data('transaction', {
            'payload': payload
        }).json()

        if callback:
            self.response_callbacks[response['message_id']] = callback

        return response
        


    def _poll_responses(self):
        """
        This function polls HPIT for responses to messages we submitted earlier on.

        Hooks:
            self.pre_poll_responses - If set to a callable, will be called before the poll
            request is made to HPIT.
            self.post_poll_responses - If set to a callable, will be called after the poll
            request is made to HPIT.

        Returns: dict - The list of responses from the server for earlier messages 
        submitted by this message sender to HPIT.
        """
        if not self._try_hook('pre_poll_responses'):
            return False

        responses = self._get_data('response/list')['responses']

        if not self._try_hook('post_poll_responses'):
            return False

        return responses


    def _dispatch_responses(self, responses):
        """
        This function is responsible for dispatching responses to earlier message to
        their callbacks that were set when the transcation was sent with self.send.

        Hooks:
            self.pre_dispatch_responses - If set to a callable, will be called before the 
            responses are dispatched to their respective callbacks.
            self.post_dispatch_responses - If set to a callable, will be called after the
            responses are dispatched to their respective callbacks.

        Returns: boolean - True if event loop should continue. False if event loop should 
            abort.
        """
        if not self._try_hook('pre_dispatch_responses'):
            return False

        for res in responses:
            try:
                message_id = res['message']['message_id']
            except KeyError:
                self.send_log_entry('Invalid response from HPIT. No message id supplied in response.')
                continue

            try:
                response_payload = res['response']
            except KeyError:
                self.send_log_entry('Invalid response from HPIT. No response payload supplied.')
                continue

            if message_id not in self.response_callbacks:
                self.send_log_entry('No callback registered for message id: ' + message_id)
                continue

            if not callable(self.response_callbacks[message_id]):
                self.send_log_entry("Callback registered for transcation id: " + message_id + " is not a callable.")
                continue
                
            self.response_callbacks[message_id](response_payload)

        if not self._try_hook('post_dispatch_responses'):
            return False

        return True

    #Plugin or Tutor can query Message Owner
    def get_message_owner(self, message_name):
        """
        Sends a blocking request to the HPIT server to get information about who will recieve
        a particular message that is sent through the system.

        Returns:
            entity_id - The owner of the message.
            None - No one "owns" this message.

        Throws:
            AuthenticationError - This entity is not signed into HPIT.
            InvalidParametersError - message_name is empty or None
        """
        if not message_name:
            raise InvalidParametersError('message_name is empty or None')

        if not isinstance(message_name, str):
            raise InvalidParametersError('message_name must be a string')

        try:
            response = self._get_data('/'.join(['message-owner', message_name]))
        except ResourceNotFoundError:
            return None

        return response['owner']

        
    #Plugin or Tutor can be Resource Owner
    def share_resource(self, resource_token, other_entity_ids):
        """
        Sends a blocking request to the HPIT server to share a particular resource with entities
        other than it's original owner. Only the resource owner can send this request. Once a plugin
        tells HPIT who the owner of a resource is, only that owner (NOT THE PLUGIN) can make this
        request.

        Input:
            resource_token - The resource token, as assigned by HPIT in a secure_resource request.
            other_entity_ids - Other entities who may view, edit, and work with this resource.

        Returns:
            True - All went well and now the other entities can view, edit, and work with this resource.

        Throws:
            AuthenticationError - This entity is not signed into HPIT.
            InvalidParametersError - The resource_token or other_entity_ids is invalid or empty.
            AuthorizationError - This entity is not the owner of this resource.
        """
        if not resource_token:
            raise InvalidParametersError('resource_token is empty or None')

        if not other_entity_ids:
            raise InvalidParametersError('other_entity_ids is empty or None')

        if not isinstance(resource_token, str):
            raise InvalidParametersError('message_name must be a string')

        if not isinstance(other_entity_ids, str) and not isinstance(other_entity_ids, list):
            raise InvalidParametersError('other_entity_ids must be a string or a list')

        response = self._post_data('share-resource', {
            'resource_id': resource_token,
            'other_entity_ids': other_entity_ids
        })

        if 'error' in response and response['error'] == 'not owner':
            raise AuthorizationError('This entity is not the owner of this message.')

        #Bad responses will cause an exception. We can safely just return true.
        return True
