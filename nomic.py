import difflib
import json
import os
import random
import subprocess
import sys

RULEBOOK = 'nomic.py'
SCORES_FILE = 'scores.json'


def get_rules():
    with open(RULEBOOK, 'r') as f:
        return f.read()


def update_rules(rules):
    with open(RULEBOOK, 'w') as f:
        f.write(rules)


def get_new_rules_proposal():
    old_rules = get_rules()
    subprocess.call([os.environ['EDITOR'], RULEBOOK])
    proposed_rules = get_rules()
    update_rules(old_rules)
    return proposed_rules


def invoke_rules(players):
    return subprocess.call([sys._base_executable, RULEBOOK] + players[1:] + [players[0]])


def take_vote(players):
    votes = list(map(lambda p: input(f'{p}\'s vote: ').lower(), players))
    counts = {vote: votes.count(vote) for vote in votes}
    plurality_winner = random.choice([vote for vote, count in counts.items()
                                      if count == max(counts.values())])
    input(f'Result: {plurality_winner}.')
    return plurality_winner


def diff_lines(old, new):
    return '\n'.join(difflib.context_diff(old.splitlines(), new.splitlines()))


if len(sys.argv) < 2:
    print('usage: python3 nomic.py player_1 [player_2 ...]')
    sys.exit(1)

players = sys.argv[1:]  # Encodes the turn order, with players[0] going first
initial_rules = get_rules()

if os.path.exists(SCORES_FILE):
    with open(SCORES_FILE, 'r') as f:
        scores = json.load(f)
else:
    scores = {player: 0 for player in players}
roll = random.randint(1, 6)
scores[players[0]] += roll
with open(SCORES_FILE, 'w') as f:
    json.dump(scores, f)

for player in players:
    if scores[player] >= 100:
        print(f'{player} wins!')
        os.remove(SCORES_FILE)
        sys.exit(0)

input(f'{players[0]}\'s turn.\nRoll: {roll}.\nScores: {scores}.')
current_vote = 'modify'
while current_vote == 'modify':
    new_rules_proposal = get_new_rules_proposal()
    update_rules(new_rules_proposal)
    print(diff_lines(initial_rules, new_rules_proposal))
    current_vote = take_vote(players[1:])  # All other players vote

if current_vote != 'accept':
    update_rules(initial_rules)

if invoke_rules(players):  # If a change causes an error code, it is reverted
    update_rules(initial_rules)
    invoke_rules(players)
