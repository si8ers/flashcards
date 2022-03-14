import json
import random
import sys
import argparse
from io import StringIO


class FlashCards:
    commands = ('add', 'remove', 'import', 'export', 'ask', 'exit', 'log', 'hardest card', 'reset stats')

    def __init__(self):
        self.cards = []
        self.log = []

    def print(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):
        _stringio = StringIO()
        print(*objects, sep=sep, end=end, file=_stringio, flush=flush)
        print(*objects, sep=sep, end=end, file=file, flush=flush)
        self.log.append(_stringio.getvalue())
        del _stringio

    def input(self, prompt=''):
        value = input(prompt)
        self.log.append(f'{prompt}> {value}\n')
        return value

    def search(self, value=None, by='term'):
        len_cards = len(self.cards)
        if by in ('term', 'definition'):
            for i in range(len_cards):
                if self.cards[i][by] == value:
                    return i
            return None
        if by == 'max':
            max_wrong = 0
            index = []
            for i in range(len_cards):
                if max_wrong > self.cards[i]['wrong']:
                    continue
                if max_wrong < self.cards[i]['wrong']:
                    max_wrong = self.cards[i]['wrong']
                    index = []
                if max_wrong > 0:
                    index.append(i)
            return index
        return None

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--import_from', default='')
        parser.add_argument('--export_to', default='')
        args = parser.parse_args()

        if args.import_from > '':
            self.command('import', file_name=args.import_from)
        go = True
        while go:
            go = self.command(self.menu())
            if go:
                self.print()
        if args.export_to > '':
            self.command('export', file_name=args.export_to)

    def menu(self):
        command = ''
        while command not in self.commands:
            self.print('Input the action ({}):'.format(', '.join(self.commands)))
            command = self.input()
        return command

    def command(self, name, file_name=None):
        len_cards = len(self.cards)
        if name == 'add':
            term = self.input(f'The card:\n')
            while self.search(value=term) is not None:
                term = self.input(f'The card "{term}" already exists. Try again:\n')
            definition = self.input(f'The definition of the card:\n')
            while self.search(value=definition, by='definition') is not None:
                definition = self.input(f'The definition "{definition}" already exists. Try again:\n')
            self.cards.append({'term': term, 'definition': definition, 'wrong': 0})
            self.print(f'The pair ("{term}":"{definition}") has been added.')
            return True
        if name == 'remove':
            term = self.input(f'Which card?\n')
            index = self.search(value=term)
            if index is None:
                self.print(f'Can\'t remove "{term}": there is no such card.')
            else:
                self.cards.pop(index)
                self.print('The card has been removed.')
            return True
        if name == 'import':
            if file_name is None:
                file_name = self.input(f'File name:\n')
            try:
                with open(file_name, 'rt') as file:
                    loading = json.load(file)
            except FileNotFoundError:
                self.print('File not found.')
                return True
            len_loading = len(loading)
            for i in range(len_loading):
                card = loading[i]
                index = self.search(card['term'])
                if index is None:
                    self.cards.append(card)
                else:
                    self.cards[index] = card
            self.print(f'{len_loading} cards have been loaded.')
            return True
        if name == 'export':
            if file_name is None:
                file_name = self.input(f'File name:\n')
            with open(file_name, 'wt') as file:
                json.dump(self.cards, file)
            self.print(f'{len_cards} cards have been saved.')
            return True
        if name == 'ask':
            n = int(self.input('How many times to ask?\n'))
            while n > 0:
                n -= 1
                i = random.randint(0, len_cards - 1)
                term = self.cards[i]['term']
                definition = self.cards[i]['definition']
                answer = input(f'Print the definition of "{term}":\n')
                if answer == definition:
                    self.print('Correct!')
                else:
                    self.cards[i]['wrong'] += 1
                    index = self.search(value=answer, by='definition')
                    if index is None:
                        self.print(f'Wrong. The right answer is "{definition}".')
                    else:
                        other = self.cards[index]['term']
                        self.print(f'Wrong. The right answer is "{definition}", but your definition is correct for "{other}".')
            return True
        if name == 'exit':
            self.print('Bye bye!')
            return False
        if name == 'log':
            file_name = self.input(f'File name:\n')
            with open(file_name, 'wt') as f:
                print(''.join(self.log), file=f)
            self.print('The log has been saved.')
            return True
        if name == 'hardest card':
            hard_cards = self.search(by='max')
            hard_len = len(hard_cards)
            if hard_len == 0:
                self.print('There are no cards with errors.')
            elif hard_len == 1:
                card = self.cards[hard_cards[0]]
                self.print('The hardest card is "{}". You have {} errors answering it.'.format(card['term'], card['wrong']))
            else:
                card = self.cards[hard_cards[0]]
                terms = '", "'.join([self.cards[x]['term'] for x in hard_cards])
                self.print('The hardest card are "{}". You have {} errors answering them.'.format(terms, card['wrong']))
            return True
        if name == 'reset stats':
            for i in range(len_cards):
                self.cards[i]['wrong'] = 0
            self.print('Card statistics have been reset.')
            return True


fc = FlashCards()
fc.run()
