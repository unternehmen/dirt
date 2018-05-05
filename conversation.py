import re

def drop_all(L, elems):
    '''Return a copy of L, dropping all the elements found in elems.
    
    :param list L: A list
    :param list elems: A list of elements to drop from *L*
    :returns: A list like *L* but without everything in *elems*
    :rtype: list
    '''
    new_list = []
    for obj in L:
        if obj not in elems:
            new_list.append(obj)
    return new_list

class Verb(object):
    '''A pattern that matches player input and extracts important information.
    
    A convenient subclass is the :class:`SimpleMatchingVerb` class.'''
    
    def match(self, msg):
        '''Attempt to match the player's input.
        
        :param str msg: The player's input
        :returns: A three-element tuple (success, args, kwargs), where success
                  is a boolean indicating whether matching was successful,
                  args is a list of arguments to pass to the verb rule's
                  callback and kwargs is a list of keyword arguments to pass
                  to the verb rule's callback.
        :rtype: tuple
        '''
        return False, None, None

class SimpleMatchingVerb(Verb):
    '''A pattern that matches simple commands with no arguments.
    
    :ivar possible_matches: The strings that this pattern will match
    :vartype possible_matches: list of strings
    '''
    def __init__(self, possible_matches):
        self.possible_matches = possible_matches
    
    def match(self, msg):
        if msg in self.possible_matches:
            return True, [], {}
        return False, None, None

class LogEntry(object):
    '''The superclass of log entries. Examples of log entry types are
    :class:`PlayerMsgLogEntry`, :class:`NPCMsgLogEntry`,
    and :class:`NarrativeLogEntry`.
    
    Log entry objects are not usually appended directly to
    the *log* instance variable in :class:`Conversation` objects.
    Instead, convenient methods such as :func:`Conversation.log_player_msg`
    are used to add to the log for that particular conversation.
    '''
    pass

class PlayerMsgLogEntry(LogEntry):
    '''A log entry representing a message from the player.
    
    :ivar str msg: The text of the player's message
    '''
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return str(self.msg)

class NPCMsgLogEntry(LogEntry):
    '''A log entry representing a message from an NPC.
    
    :ivar str name: The name of the NPC
    :ivar str msg: The text of the NPC's message
    '''
    def __init__(self, name, msg):
        self.name = name
        self.msg = msg
        
    def __str__(self):
        return str('%s: %s' % (self.name, self.msg))

class NarrativeLogEntry(LogEntry):
    '''A log entry representing a passage of text that is not dialogue.
    
    :ivar str msg: The text of the passage
    '''
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        '''Returns the message stored inside this log entry.'''
        return str(self.msg)

class Rule(object):
    '''A rule for interpreting player input in a conversation. The
    only rule type is a :class:`TopicRule`.
    '''
    pass

_ask_about_regex = re.compile('^ask ((.+?) )?about (.+)$')
_what_about_regex = re.compile('^what about (.+)$')
_know_about_regex = re.compile('^(do you know|i want to know) about (.+)$')
class TopicRule(Rule):
    '''A topic rule describes a generic topic of conversation. Players
    can type "ASK ABOUT <TOPIC>", "WHAT ABOUT <TOPIC>",
    "I WANT TO KNOW ABOUT <TOPIC>", or "<TOPIC>" to activate this rule.
    
    :ivar str canonical_name: The canonical name of the topic
    :ivar synonyms: Synonyms for the topic
    :vartype synonyms: list of strings
    :ivar function callback: A function to be called when this rule is activated
    '''
    def __init__(self, canonical_name, synonyms, callback):
        self.canonical_name = canonical_name
        self.synonyms = synonyms
        self.callback = callback
    
    def activate(self, msg, conversation, player):
        '''Attempts to activate the rule with a piece of player input.
        
        :param str msg: The player input
        :param Conversation conversation: The conversation that this rule belongs to
        :param dirt.Player player: The player
        :returns: True if the rule activates successfully, False otherwise
        :rtype: bool
        '''
        # Clean the player input for ease of processing
        msg = msg.lower()
        words = _word_seperator_regex.split(msg)
        words = drop_all(words, ['the'])
        msg = ' '.join(words)
        msg = msg.strip()
        
        # Try to activate
        noun = None
        m = _ask_about_regex.match(msg)
        if m:
            noun = m.group(3)
        else:
            m = _what_about_regex.match(msg)
            if m:
                noun = m.group(1)
            else:
                m = _know_about_regex.match(msg)
                if m:
                    noun = m.group(2)
                else:
                    noun = msg
        
        if noun == self.canonical_name or noun in self.synonyms:
            self.callback(conversation, player)
            return True
        
        return False

_word_seperator_regex = re.compile('[.!?, ]+')

class VerbRule(Rule):
    '''A verb rule describes a more freeform command than the topic system.
    With verb rules, you accept more complex commands such as "HEY",
    "BOW TO JYESULA", or "GIVE RING TO JYESULA".
    
    :ivar Verb verb: The verb object that this rule matches with
    :ivar function callback: A function to be called when this rule activates
    '''
    def __init__(self, verb, callback):
        self.verb = verb
        self.callback = callback
    
    def activate(self, msg, conversation, player):
        '''Attempts to activate the rule with a piece of player input.
        
        :param str msg: The player input
        :param Conversation conversation: The conversation that this rule belongs to
        :param dirt.Player player: The player object
        :returns: True if the rule activates successfully, False otherwise
        :rtype: bool
        '''
        # Clean the player input for ease of processing
        msg = msg.lower()
        words = _word_seperator_regex.split(msg)
        words = drop_all(words, ['the'])
        msg = ' '.join(words)
        msg = msg.strip()
        
        # Try to activate
        success, args, kwargs = self.verb.match(msg)
        if success:
            self.callback(conversation, player, *args, **kwargs)
            return True
        
        return False

class Conversation(object):
    '''A Conversation object contains the underlying logic of a
    conversation.
    
    :ivar str default_npc_name: The default name attached to logged NPC messages
    :ivar log: The log of messages that have appeared in this conversation
    :vartype log: list of :class:`LogEntry`
    :ivar rules: All the rules governing the conversation
    :vartype rules: list of :class:`Rule`
    '''
    def __init__(self, default_npc_name):
        self.default_npc_name = default_npc_name
        self.log = []
        self.rules = []
    
    def prune_log(self):
        '''Prunes the log to the most recent 5 messages.'''
        if len(self.log) > 5:
            self.log = self.log[-5:]
    
    def log_player_msg(self, msg):
        '''Appends a :class:`PlayerMsgLogEntry` to the log of this
        conversation.
        '''
        self.log.append(PlayerMsgLogEntry(msg))
        self.prune_log()
    
    def log_npc_msg(self, msg, name=None):
        '''Appends a :class:`NPCMsgLogEntry` to the log of this
        conversation.
        '''
        if name is None:
            name = self.default_npc_name
        self.log.append(NPCMsgLogEntry(name, msg))
        self.prune_log()
    
    def log_narrative(self, msg):
        '''Appends a :class:`NarrativeLogEntry` to the log of this
        conversation.
        '''
        self.log.append(NarrativeLogEntry(msg))
        self.prune_log()
    
    def feed_player_msg(self, msg, player):
        '''Feeds a message from the user to this conversation object.
        Typically, this will elicit a response based on the methods
        implemented by this conversation object.
        
        The message will automatically be logged.
        
        :param str msg: The user's message
        :param dirt.Player player: The player object
        '''
        self.log_player_msg(msg)
        for rule in self.rules:
            if rule.activate(msg, self, player):
                break
    
    def verb(self, name):
        '''A decorator which adds a verb handler to the conversation rules.
        
        :param str name: The name of the verb.
        '''
        def verb_wrapper(func):
            self.rules.append(VerbRule(name, func))
            return func
        
        return verb_wrapper
    
    def topic(self, canonical_name, *synonyms):
        '''Returns a decorator which adds a topic to the conversation rules.
        
        :param str canonical_name: The canonical name of the topic.
        :param synonyms: A list of synonyms for the topic.
        :type synonyms: list of strings
        '''
        def topic_wrapper(func):
            self.rules.append(TopicRule(canonical_name, synonyms, func))
            return func
        
        return topic_wrapper
