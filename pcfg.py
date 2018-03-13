#! /usr/bin/env python3

import sys
import string
from queue import PriorityQueue
from collections import defaultdict as ddict


class Pcfg:
    def __init__(self):
        # If letter is not lower or digit it's special
        self.type = ddict(lambda: 'S')
        for alpha in string.ascii_letters:
            self.type[alpha] = 'L'
        for digit in string.digits:
            self.type[digit] = 'D'
        self.base = ddict(float)
        self.terminals = ddict(dict)
        self.ordered_terms = dict()

    def learn(self, filename):
        with open(filename) as _buffer:
            for word in _buffer:
                word = word.rstrip('\n\r')
                self.parse(word)
        nb_bases = sum(self.base.values())
        for _str, proba in self.base.items():
            self.base[_str] = proba / nb_bases

        for _str, term_proba in self.terminals.items():
            nb_terms = 0
            for term, proba in term_proba.items():
                nb_terms += proba
            for term, proba in term_proba.items():
                term_proba[term] = proba / nb_terms

    def parse(self, word):
        if len(word) == 0:
            return
        chain = list()
        curr_str = ""
        for index, char in enumerate(word):
            t = self.type[char]
            if index == 0:
                chain.append([t, 1])
                curr_str += char
                continue
            # type-string is growing
            if t == self.type[curr_str[-1]]:
                chain[-1][1] += 1
                curr_str += char
            else:
                # L3, S1, D4, ...
                type_str = ''.join([str(it) for it in chain[-1]])
                # we don't care of alpha terminals
                if type_str[0] != 'L':
                    if curr_str in self.terminals.keys():
                        self.terminals[type_str][curr_str] += 1
                    else:
                        self.terminals[type_str][curr_str]  = 1
                curr_str = char
                chain.append([self.type[char], 1])
            if index == len(word)-1:
                # L3, S1, D4, ...
                type_str = ''.join([str(it) for it in chain[-1]])
                # we don't care of alpha terminals
                if type_str[0] != 'L':
                    if curr_str in self.terminals.keys():
                        self.terminals[type_str][curr_str] += 1
                    else:
                        self.terminals[type_str][curr_str]  = 1

        base = '_'.join([_type+str(occ) for _type, occ in chain])
        self.base[base] += 1

    def enumpwd(self, rate=0.1):
        pq = PriorityQueue()
        # init priority queue
        for index, (base, proba) in enumerate(sorted(self.base.items(), key=lambda x:x[1], reverse=True)):
            if (index/len(self.base)) > rate:
                break
            preterm = list()
            prob = proba
            for _type_str in base.split('_'):
                if _type_str[0] == 'L':
                    preterm.append(_type_str)
                    continue
                term_probas = self.terminals[_type_str]
                highest = max(term_probas.items(), key=lambda x:x[1])
                preterm.append(highest[0])
                proba *= highest[1]
            pq.put((1-proba, base, preterm, 0))

        # start enumeration
        while not pq.empty():
            prob, base, preterm, pivot = pq.get()
            prob = 1-prob
            self.print(preterm)
            type_str = base.split('_')
            for index in range(pivot, len(type_str)):
                cur_term = preterm[index]
                if cur_term[0] == 'L': continue
                cur_term_proba = self.terminals[type_str[index]][cur_term]
                _next = self.next(type_str[index], cur_term)
                if _next is None: continue
                next_term, proba = _next
                preterm[index] = next_term
                prob /= cur_term_proba
                prob *= proba
                pq.put((1-prob, base, preterm, index))

    def next(self, type_str, cur_term):
        if type_str in self.ordered_terms:
            ordered_terms = self.ordered_terms[type_str]
        else:
            ordered_terms = sorted(self.terminals[type_str].items(), key=lambda x:x[1])
            self.ordered_terms[type_str] = ordered_terms
        if cur_term == ordered_terms[-1][0]:
            return None
        for index, (term, proba) in enumerate(ordered_terms):
            if term == cur_term:
                break
        return ordered_terms[index+1]

    def print(self, preterm):
        print('_'.join(preterm))

if __name__ == '__main__':
    filename = sys.argv[1]
    pcfg = Pcfg()
    print('parsing ...', file=sys.stderr)
    pcfg.learn(filename)
    print('enum ...', file=sys.stderr)
    pcfg.enumpwd()
