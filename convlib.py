'''Conversation rules for main characters.'''

from conversation import Conversation, SimpleMatchingVerb

# Verb definitions

_verb_hello = SimpleMatchingVerb(['hello', 'yo', 'ho there', 'hey', 'hi', 'what\'s up', 'whats up', 'sup',
                                 'hail', 'greetings', 'salutations', 'wassup', 'whassup', 'what\'s good',
                                 'whats good'])
_verb_bye = SimpleMatchingVerb(['bye', 'goodbye', 'good-bye', 'see you', 'see you later',
                                'later', 'see ya', 'see ya later', 'farewell'])
_verb_bow = SimpleMatchingVerb(['bow', 'bow down', 'submit'])

# Character - JYESULA

jyesula = Conversation('Jyesula')

@jyesula.begin
def _jyesula_begin(c, ply, circumstances, *args, **kwargs):
    if circumstances == 'throneroom':
        c.log_narrative('The Chairman acknowledges your presence\nbut his attention is on a\nmeter-high stack of census reports.')

@jyesula.verb(_verb_hello)
def _jyesula_v_hello(c, ply):
    c.log_npc_msg('Hail, comrade.')

@jyesula.verb(_verb_bye)
def _jyesula_v_bye(c, ply):
    c.log_npc_msg('Farewell, comrade.')
    ply.in_conversation = False

@jyesula.verb(_verb_bow)
def _jyesula_v_bow(c, ply):
    c.log_narrative('Jyesula chuckles.')
    c.log_npc_msg('You are learning manners, I see.')

@jyesula.topic('jyesula', 'jyesul', 'jyesula dy chief', 'our lord',
               'yourself', 'you', 'lord', 'milord', 'my lord', 'chairman', 'chair man')
def _jyesula_t_jyesula(c, ply):
    c.log_npc_msg('My empire knows no limit.\nYou are safe here, Jauld.')

@jyesula.topic('cold garden', 'c g', 'cg', 'garden')
def _jyesula_t_cold_garden(c, ply):
    c.log_npc_msg('If you find my ring,\nI can return to C G.\nBut I cannot take you with me.')

@jyesula.topic('ring')
def _jyesula_t_ring(c, ply):
    c.log_npc_msg('A powerful ring was stolen by Garial dy Chief.')
    c.log_npc_msg('Find it.')

@jyesula.topic('money', 'payment', 'compensation', 'salary', 'moolah', 'gold')
def _jyesula_t_money(c, ply):
    c.log_npc_msg('You have always been fine\nwithout money.\nWhy do you need it now?')

@jyesula.topic('sun', 'day and night', 'night and day', 'day', 'night', 'daytime', 'nighttime')
def _jyesula_t_sun(c, ply):
    c.log_npc_msg('The sun goes\ndown quite\nsuddenly, yes.')

@jyesula.topic('lettre', 'letter', 'note')
def _jyesula_t_lettre(c, ply):
    c.log_npc_msg('It seems that\ndanger is afoot.\nJauld, fix it.')

@jyesula.topic('toddtest', 'toddtest json', 'data toddtest json')
def _jyesula_t_toddtest(c, ply):
    c.log_npc_msg('It will not do\nto dwell on the past.')
