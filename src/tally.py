from __future__ import annotations
from pathlib import Path
import csv

PATH_DATA = Path('src/data')

class VoteKind:
    UP: str='up'
    DOWN: str='dn'
    ACCEPT: str='ac'
    EDIT: str='ed'

    @staticmethod
    def map(s: str) -> str:
        """TODO So over-the-top LOL"""
        return {
            'up': VoteKind.UP,
            'dn': VoteKind.DOWN,
            'acc': VoteKind.ACCEPT,
            's.edit': VoteKind.EDIT
        }[s.lower()]

class UnidirectionalVoteRecord:
    fr: User
    to: User
    votes: dict[str, int]

    def __init__(self: UnidirectionalVoteRecord, fr: User, to: User):
        self.fr = fr
        self.to = to
        self.votes = init_vote_totals_dict()
    
    def __hash__(self: UnidirectionalVoteRecord) -> int:
        return hash(f'{self.fr} > {self.to}')

class User:
    """
    Although vote totals are in theory derivable from VRs, since we're looking at one user's page
    at a time, it's possible to get them from an individual VR where they're listed anyway.
    e.g. Anne has a VR received from Bob. dn: 58 / 700. Here, we learn Bob's total dn vote count of 700
    even though our main user is Anne. To derive that count naturally, we would also need to look at Bob's
    user page and examine all his give VRs. So we can just note it while we're looking at Anne's.
    """
    name: str
    vote_received_totals: dict[str, int]
    vote_given_totals: dict[str, int]
    vrs_received: set[UnidirectionalVoteRecord]    
    vrs_given: set[UnidirectionalVoteRecord]

    def __init__(self: User, name: str):
        self.name = name
        self.vote_received_totals = init_vote_totals_dict()
        self.vote_given_totals = init_vote_totals_dict()
        self.vrs_received = set()
        self.vrs_given = set()

    def __hash__(self: User) -> int:
        return hash(self.name)
    
    def __repr__(self: User) -> str:
        return self.name

def init_vote_totals_dict() -> dict[str, int]:
    return {kind: 0 for kind in (VoteKind.UP, VoteKind.DOWN, VoteKind.ACCEPT, VoteKind.EDIT)}

def parse_name(s: str) -> tuple[str, str]:
    """
    Returns name and reputation as a tuple.
    Names with numbers at the end have a comma separating them from the reputation int.
    Otherwise, the reputation int is appended directly to the end of the name.

    TODO The delimiter and quotation or lack thereof may depend on how the CSV was saved.
    This was done by copying straight into the CSV editor in whatever VSCode extension it is I have installed,
    then removing the 5th column that has line breaks in it (x-ips, etc).

    TODO Also, right now the reputation is the score and the badge counts all in one str.
    Not parsing them out because I don't really care for these purposes.
    """
    if ',' in s:
        name, rep = s.split(',')
        return name, rep
    
    else:
        for i in range(len(s)):
            if s[i].isdigit():
                return s[:i], s[i:]

def parse_received(mu: User, users: dict[str, User]):
    """
    Read the received file and update mu and users in place.
    """
    path = PATH_DATA / f'{mu.name}-received.csv'
    if not path.exists():
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        rows = csv.reader(f, delimiter=';')
        next(rows) # Headers

        for row in rows:
            cells = list(c.strip() for c in row)

            # Start new user on rows that have a username
            if cells[0]:
                name, _ = parse_name(cells[0])
                u = users.setdefault(name, User(name))

                vr = UnidirectionalVoteRecord(u, mu)
                u.vrs_given.add(vr)
                mu.vrs_received.add(vr)
            
            # All rows have the vote kind and count
            kind = VoteKind.map(cells[1])
            num, denom = (int(c) for c in cells[2].split(' / '))
            vr.votes[kind] = num
            u.vote_given_totals[kind] = denom

    # From the received counts, we can also glean the given by each voting user
    for vr in mu.vrs_received:
        for k in vr.votes:
            mu.vote_received_totals[k] += vr.votes[k]

def parse_given(mu: User, users: dict[str, User]):
    """
    Read the given file and update mu and users in place.
    """
    path = PATH_DATA / f'{mu.name}-given.csv'
    if not path.exists():
        return
    
    with open(path, 'r', encoding='utf-8') as f:
        rows = csv.reader(f, delimiter=';')
        next(rows) # Headers

        for row in rows:
            cells = list(c.strip() for c in row)

            # Start new user on rows that have a username
            if cells[0]:
                name, _ = parse_name(cells[0])
                u = users.setdefault(name, User(name))

                vr = UnidirectionalVoteRecord(mu, u)
                mu.vrs_given.add(vr)
                u.vrs_received.add(vr)
            
            # All rows have the vote kind and count
            kind = VoteKind.map(cells[1])
            num, denom = (int(c) for c in cells[2].split(' / '))
            vr.votes[kind] = num
            mu.vote_given_totals[kind] = denom

def get_er(vr: UnidirectionalVoteRecord) -> float:
    dv = vr.votes[VoteKind.DOWN]
    total = sum(vr.votes.values())
    if not total:
        return 0
    else:
        return (dv / total) * 100

def report(mu: User, users: dict[str, User]):
    """
    mu = main user, the user's page we're targeting
    """
    parse_received(mu, users)
    parse_given(mu, users)

    print()
    print(f'{mu.name} votes given:', mu.vote_given_totals)
    print(f'{mu.name} votes received:', mu.vote_received_totals)
    
    # ad hoc attribute er = 'evil ratio', or ratio of dv to total
    for vr in mu.vrs_given.union(mu.vrs_received):
        vr.er = get_er(vr)

    print()

    print(f'People {mu.name} has the highest dv ratio towards')
    for vr in sorted(mu.vrs_given, key=lambda vr: -vr.er)[:10]:
        print(f'{vr.er:<6.2f}% {vr.votes[VoteKind.DOWN]:>4}:{vr.votes[VoteKind.UP]:<4} {vr.to}')

    print()

    print(f'People {mu.name} has the highest dv ratio from')
    for vr in sorted(mu.vrs_received, key=lambda vr: -vr.er)[:10]:
        print(f'{vr.er:<6.2f}% {vr.votes[VoteKind.DOWN]:>4}:{vr.votes[VoteKind.UP]:<4} {vr.fr}')

def report_one(name: str) -> None:
    user = User(name)
    users = {name: user}
    report(user, users)

def report_all() -> None:
    names = set()
    for path in PATH_DATA.glob('*.csv'):
        # Chop off final '-given' or '-received'
        name = '-'.join(path.stem.split('-')[:-1])
        names.add(name)
        
    for name in sorted(names):
        report_one(name)

def run():
    name = input('Enter username of account in question, or * for all: ').strip()
    if name == '*':
        report_all()
    else:
        report_one(name)

if __name__ == '__main__':
    run()
