"""
Author: Matthew Garber
Term: Spring 2017
COSI 137b Information Extraction
Assignment #4

This module contains classes for representing enitity mentions and relations.
There is a Mention class, to model entity mentions, and a Relation class, to
model relations between to entity mentions.
"""

from nltk.corpus import stopwords
from tree_util import get_path

STOPWORDS = set(stopwords.words('english'))

class Relation:
    """Objects of this class represent relations between two enitity mentions.
    It possesses methods to extract features from the mentions, as well as
    their contexts. It also contains a method to write its features as a string
    in the format of a MALLET instance.
    """

    def __init__(self, values, sents, sent_trees, rel_id):
        """Initializes a new Relation object.

        Args:
            values: A list of values containing information about the relation
                and the enitities it relates.
            sents: A list of a list of 3-tuples representing words in the
                sentences of a document.
            sent_trees: A list of parse trees extraced from the same document.
            rel_id: The ID number of the relation
        """
        self.rel_type = values[0]
        self.m1 = Mention(*values[2:8], sents=sents)    # mention 1
        self.m2 = Mention(*values[8:], sents=sents)     # mention 2

        if self.m1.sent_i == self.m2.sent_i:
            self.tree = sent_trees[self.m1.sent_i]
            self.in_same_sent = True
        else:
            self.tree = None
            self.in_same_sent = False
        
        self._find_words_before_m1(sents)
        self._find_words_after_m2(sents)
        self._find_words_between(sents)

        self._find_phrase_features(sents)

        self._find_phrase_dist()
        
        self.rel_id = str(rel_id)
        

    def to_string(self):
        """Uses this objects attributes to derive and write its features as a
        string formatted as a MALLET instance.
        """
        feats = []
        
        # --- Word Features ---
        # Bag-of-words
        feats.extend(['WE1=' + word for word in self.m1.word_set])
        feats.extend(['WE2=' + word for word in self.m2.word_set])
        
        # Words preceding mention 1 + entity type
        feats.append('BM1F=' + self.pre1_m1[0] + self.m1.ner_tag)
        feats.append('BM1L=' + self.pre2_m1[0] + self.m1.ner_tag)
        # Words following mention 2 + entity type
        feats.append('AM2F=' + self.post1_m2[0] + self.m2.ner_tag)
        feats.append('AM2L=' + self.post2_m2[0] + self.m2.ner_tag)
        
        # No words in between
        feats.append('WBNULL=' + str(self.adjacent))
        # Single word in between
        feats.append('WBONLY=' + self.only_word_between)
        # First and last word in between
        feats.append('WBF=' + self.first_between)
        feats.append('WBL=' + self.last_between)
        # Other words between
        words_between = set([vals[0] for vals in self.vals_between])
        feats.extend(['WBO=' + word for word in words_between])
        
        # --- Head Word / Phrase Features ---
        # Mention head words
        feats.append('HM1=' + self.m1.head_word)
        feats.append('HM2=' + self.m2.head_word)
        # Mention head word conjunction
        feats.append(''.join(['HM12=', self.m1.head_word + '_', self.m2.head_word]))
        
        # Mention head POS
        feats.append('HPOSM1=' + self.m1.head_pos)
        feats.append('HPOSM2=' + self.m2.head_pos)
        # Mention head POS conjunction
        feats.append(''.join(['HPOSM12=', self.m1.head_pos + '_', self.m2.head_pos]))

        # Mention head word + POS
        feats.append(''.join(['HWPOSM1=', self.m1.head_word + '_', self.m1.head_pos]))
        feats.append(''.join(['HWPOSM2=', self.m2.head_word + '_', self.m2.head_pos]))
        
        # No heads in between
        feats.append('CHBNULL=' + str(self.in_same_sent and len(self.heads_between) == 0))

        # Single head in between
        if len(self.heads_between) == 1:
            # Head word
            feats.append('CHBONLY=' + self.heads_between[0][0])
            # Head POS
            feats.append('CHBONLY_POS=' + self.heads_between[0][1])
        else:
            feats.append('CHBONLY=' + '*null*')
            feats.append('CHBONLY_POS=' + '*null*')

        # First and last head word between
        if len(self.heads_between) > 1:
            feats.append('CHBF=' + self.heads_between[0][0])
            feats.append('CHBL=' + self.heads_between[-1][0])
        else:
            feats.append('CHBF=' + '*null*')
            feats.append('CHBL=' + '*null*')

        # Last head word before mention 1
        feats.append('CHPM1=' + self.prev_head[0])
        # Next head word after mention 2
        feats.append('CHNM2=' + self.next_head[0])
        
        # Phrase/Chunk distance
        if self.in_same_sent:
            feats.append('CHDIST=' + self.phrase_dist)
        else:
            feats.append('CHDIST=' + '*null*')
        
        # --- Entity type conjuction ---
        feats.append(''.join(['ET12=', self.m1.ner_tag, self.m2.ner_tag]))
        
        # --- Overlap Features ---
        # Simple overlap
        feats.append('M1>M2=' + str(self.m1.contains(self.m2)))
        feats.append('M1<M2=' + str(self.m2.contains(self.m1)))
        # Overlap + entity type conjunction
        feats.append('M1>M2+E12=' + '_'.join([str(self.m1.contains(self.m2)), self.m1.ner_tag, self.m2.ner_tag]))
        feats.append('M1<M2+E12=' + '_'.join([str(self.m2.contains(self.m1)), self.m1.ner_tag, self.m2.ner_tag]))        
        # Number of words between
        feats.append('#WB=' + str(len(self.vals_between)))
        
        # --- Parse Tree Features ---
        if self.tree == None:
            #feats.append('PATH=' + '*null*')
            feats.append('SHORTPATH=' + '*null*')
        else:
            parse_path = get_path(self.m1.head_i, self.m2.head_i, self.tree)
            #feats.append('PATH=' + ','.join(parse_path))
            feats.append('SHORTPATH=' + ','.join(parse_path[1:-1]))
            top_node = None
            for node in parse_path:
                if node.endswith('0'):
                    top_node = node
        
        line = ' '.join([self.rel_id, self.rel_type] + feats)
        return line
        

    def _find_words_before_m1(self, sents):
        """Finds the words preceding mention 1.
        """
        sent_i = self.m2.sent_i
        if self.m1.start > 1:
            self.pre2_m1 = sents[sent_i][self.m1.start-2]
        else:
            self.pre2_m1 = '*null*'
        if self.m1.start > 0:
            self.pre1_m1 = sents[sent_i][self.m1.start-1]
        else:
            self.pre1_m1 = '*null*'

    def _find_words_after_m2(self, sents):
        """Finds the words following mention 2.
        """
        sent_i = self.m2.sent_i
        length = len(sents[sent_i])
        if self.m2.end < length:
            self.post1_m2 = sents[sent_i][self.m2.end]
        else:
            self.post1_m2 = '*null*'
        if self.m2.end + 1 < length:
            self.post2_m2 = sents[sent_i][self.m2.end+1]
        else:
            self.post2_m2 = '*null*'    

    def _find_words_between(self, sents):
        """Finds the words between mentions 1 and 2. If the mentions are in
        different sentences, a placeholder '*null*' is used instead.
        """
        if self.in_same_sent:
            sent_i = self.m1.sent_i
            self.adjacent = self.m1.end == self.m2.start
            if self.m1.end - self.m2.start == 1:
                self.only_word_between = sents[sent_i][self.m1.end][0]
            else:
                self.only_word_between = '*null*'
            if self.m1.end - self.m2.start > 1:
                self.first_between = sents[sent_i][self.m1.end][0]
                self.last_between = sents[sent_i][self.m2.start-1][0]
            else:
                self.first_between = '*null*'
                self.last_between = '*null*'
        else:
            self.adjacent = False
            self.only_word_between = '*null*'
            if self.m1.end < len(sents[self.m1.sent_i]):
                self.first_between = sents[self.m1.sent_i][self.m1.end][0]
            else:
                self.first_between = '*end*'
            if self.m2.start > 0:
                self.last_between = sents[self.m2.sent_i][self.m2.start-1][0]
            else:
                self.last_between = '*start*'

    def _find_phrase_dist(self):
        """Finds the number of phrases between mentions 1 and 2. If the number
        is 10 or greater, it is simply set as 'max'.
        """
        dist = len(self.heads_between)
        if dist < 10:
            self.phrase_dist = str(dist)
        else:
            self.phrase_dist = 'max'

    def _find_phrase_features(self, sents):
        """Finds various phrase features regarding mentions 1 and 2, including
        the number of heads in between
        """
        self.heads_between = []
        self.vals_between = []
        sent = sents[self.m1.sent_i]
        if (not self.adjacent and not self.m1.contains(self.m2)
                and not self.m2.contains(self.m1)):
            for i in range(self.m1.end, self.m2.start):
                vals = sent[i]
                self.vals_between.append(vals)
                if vals[2].endswith('1'):
                    self.heads_between.append(vals)
        found_prev_head = False
        start = self.m1.start - 1
        while start >= 0:
            if sent[start][2].endswith('1'):
                found_prev_head = True
                self.prev_head = sent[start]
                break
            start -= 1
        if not found_prev_head:
            self.prev_head = ('*null*', '*null*', '*null*')
            
        end = self.m2.end
        found_next_head = False
        while end < len(sent):
            if sent[end][2].endswith('1'):
                found_prev_head = True
                self.next_head = sent[start]
                break
            end += 1
        if not found_next_head:
            self.next_head = ('*null*', '*null*', '*null*')
                

class Mention:
    """Objects of this class represent single entity mentions. It possesses
    methods to extract features from the mention, as well as a method to see
    whether it contains a given mention.
    """

    def __init__(self, sent_i, start, end, ner_tag, identifier, string, sents):
        """Initializes a new Mention object.

        Args:
            sent_i: The string index of the sentence the mention occurs in.
            start: The string start index of the mention.
            end: The string end index of the mention.
            ner_tag: The NER tag of the mention.
            identifier: The string identifier of the mention.
            string: The words of the mention, as a string separated by
                underscores.
            sents: A list of a list of 3-tuples representing words in the
                sentences of a document.
        """
        self.sent_i = int(sent_i)
        self.start = int(start)
        self.end = int(end)
        self.ner_tag = ner_tag
        self.words = string.lower().split('_')
        self.word_set = set(self.words) - STOPWORDS
        self._find_head_vals(sents[self.sent_i])

    def _find_head_vals(self, sent):
        """Finds the word, POS tag, and chunk tag of the head word of the
        mention.
        """
        found_head = False
        for i in range(self.start, self.end):
            if sent[i][2].endswith('1'):
                found_head = True
        if found_head:
            self.head_word = sent[i][0]
            self.head_pos = sent[i][1]
            self.head_chunk = sent[i][2]
            self.head_i = i
        else:
            self.head_word = sent[self.end-1][0]
            self.head_pos = sent[self.end-1][1]
            self.head_chunk = sent[self.end-1][2]
            self.head_i = self.end - 1

    def contains(self, mention):
        """Returns true if the given mention is included in this mention.
        """
        if self.sent_i == mention.sent_i:
            return self.start <= mention.start and self.end >= mention.end
        else:
            return False
