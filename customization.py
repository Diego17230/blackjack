RANKS = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
         'Ten', 'Jack', 'Queen', 'King', 'Ace')
SUITS = ('♣', '♦', '♥', '♠')

if len(RANKS) != 13:
    raise ValueError("RANKS constant does not have 13 elements")
if len(SUITS) != 4:
    raise ValueError("SUITS constant does not have 4 elements")

for const in (RANKS, SUITS):
    if len(set(const)) < len(const):
        raise ValueError("Constants should have only unique elements")

