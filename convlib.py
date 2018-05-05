'''Conversation rules for main characters.'''

from conversation import Conversation, SimpleMatchingVerb

# Verb definitions

_verb_hello = SimpleMatchingVerb(['hello', 'yo', 'ho there', 'hey', 'hi', 'what\'s up',
                                 'hail', 'greetings', 'salutations'])
_verb_bye = SimpleMatchingVerb(['bye', 'goodbye', 'good-bye', 'see you', 'see you later',
                                'later', 'see ya', 'see ya later', 'farewell'])

# Character - JYESULA

jyesula = Conversation('Jyesula')

@jyesula.verb(_verb_hello)
def _jyesula_v_hello(c, ply):
    c.log_npc_msg('Hail, comrade.')

@jyesula.verb(_verb_bye)
def _jyesula_v_bye(c, ply):
    c.log_npc_msg('Farewell, comrade.')
    ply.in_conversation = False

@jyesula.topic('jyesula', 'jyesul', 'jyesula dy chief', 'our lord',
               'yourself', 'you', 'lord', 'milord', 'my lord')
def _jyesula_t_jyesula(c, ply):
    c.log_npc_msg('Ah, Jauld. My old friend.')

@jyesula.topic('cold garden', 'c g', 'cg', 'garden')
def _jyesula_t_cold_garden(c, ply):
    c.log_npc_msg('If you find my ring,\nI can return to C G.\nBut I cannot take you with me.')

@jyesula.topic('ring')
def _jyesula_t_ring(c, ply):
    c.log_npc_msg('The ring is older than I.')
