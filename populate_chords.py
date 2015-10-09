#!/usr/bin/env python
# populate the database with some meaningful data

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guitarchords.settings')
django.setup()

from chords.models import Artist, Song, User


def add_artist(name):
    a = Artist.objects.get_or_create(name=name)[0]
    a.save()
    return a

def add_song(title, artist, sender=None, content='', genre='', video='',
             tabs=False, published=False):
    s = Song.objects.get_or_create(title=title, artist=artist)[0]
    s.sender = sender
    s.content = content
    s.genre = genre
    s.video = video
    s.tabs = tabs
    s.published = published
    if published:
        s.publish()
    s.save()
    return s

def create_user(username='username', password='password'):
    try:
        user = User.objects.filter(username=username)[0]
    except IndexError:
        user = User.objects.create_user(username=username, password=password)
        user.save()

    return user

def populate():
    user_bob = create_user(username='bob', password='bob')

    artist_katsimixa = add_artist('Αδελφοί Κατσιμίχα')

    add_song(
        title='Ρίτα Ριτάκι',
        artist=artist_katsimixa,
        sender=user_bob,
        video='https://www.youtube.com/watch?v=QMyEGJNv6j4',
        genre=Song.ENTEXNO,
        content="""
G          Em        C             D
Παλεύει το ποτάμι στη θάλασσα να βγει
Κι ο ποιητής γυρεύει τη μούσα του να βρει
Το κύμα ψάχνει να ’βρει την άκρη του γιαλού
G              Em
Κι εγώ γυρεύω εσένανε
Am          C          D           (A)
εσένανε που μ’ έστησες ξανά στο ραντεβού

G               Em          C            D
Έψαχνα να ’βρω το μπελά μου και τελικά τον βρήκα
    G         Em      Am           D
Και πήγα και αγάπησα ένα μωρό, τη Ρίτα
G        Em          Am            D
Ρίτα δεκαοχτώ χρονών κι εγώ σαράντα πέντε
G              Em       Am              D
Ρίτα εσύ ’σαι στην αρχή κι εγώ στο παραπέντε

G     Em   C          D
Ρίτα-Ριτάκι, κανένα δε φοβάσαι
G      Em   C          D
Ρίτα-Ριτάκι, τίποτα δε θυμάσαι
G      Em   Am         D
Ρίτα-Ριτάκι, απόψε πού κοιμάσαι

G                Em         C          D
Μου το ’χες πει πολλές φορές ότι δε μ’ αγαπούσες
  G         Em         Am      D
Συγγνώμη, δεν κατάλαβα ότι το εννοούσες
G             Em         C              D
Γι αυτό λοιπόν σε χαιρετώ και φεύγω δίχως λόγια
G            Em        C            D
Με το κεφάλι μου ψηλά και την ψυχή στα πόδια

G     Em   C          D
Ρίτα-Ριτάκι, κανένα δε φοβάσαι
G      Em   C          D
Ρίτα-Ριτάκι, τίποτα δε θυμάσαι
G      Em   Am         D
Ρίτα-Ριτάκι, απόψε πού κοιμάσαι
""",
        published = True
            )

    artist_xasma = add_artist('Χάσμα')

    add_song(
        title='Δε με ελέγχω',
        artist=artist_xasma,
        sender=user_bob,
        video='https://www.youtube.com/watch?v=ltq7MVYz_XI',
        genre=Song.PUNK,
        content="""
                   Bm               D
Κάνουν το λάθος το απλό, μα και σωστό
                    Em
και μ' έχουν στο ξωπίσω
                    Bm                D
με λένε γιο της μοναξιάς γιατί είμαι εδώ
             G
χωρίς να φταίω εγώ
                          Bm               D
και μου ξορκίζουν τις στιγμές μ' αγνές ευχές
                 Em
μπροστά να προχωρήσω
                       G
μα εγώ το ξέρω πως θα ζήσω
             A
μόνο σαν κακή στιγμή σε κόλπο ομαδικό

Bm           D                     Em
Κι όλοι γελούν όταν το στόμα μου ανοίξω
                   Bm
μου χαρακώνουν το χτες
                D                      G
φωτεινές επιγραφές που δείχνουν το σωστό
                          Bm                  D
γιατί είσαι κι εσύ κάθε φορά που φεύγεις μακριά
                  Em
και για να σ' αγαπήσω
                             G
πρέπει απ' την αρχή να ξαναρχίσω
                    A
μα φταίει μόνο που δε με ελέγχω
Bm            Em             A      Em
δε με ελέγχω, δε με ελέγχω, δε με ελέγχω

    Bm
Και τρέχω - χάνομαι - μπλέκω σε γιορτή
ανησυχώ - ζαλίζομαι - γίνομαι κελί
κάθε στιγμή που αφήνομαι να σε κοιτώ απλά
        G
σα ναυαγός ξεβράζομαι μες τη μοναξιά

Bm
Τρέχω - χάνομαι - μπλέκω σε γιορτή
ανησυχώ - ζαλίζομαι - γίνομαι κελί
κάθε στιγμή που αφήνομαι να σε κοιτώ απλά
        G
δε με ελέγχω - χάνομαι - γίνομαι σκιά

        Bm
Δε με ελέγχω - μπλέκω σε γιορτή
        D
δε με ελέγχω - γίνομαι κελί
        A
δε με ελέγχω - να σε κοιτώ απλά
        G
δε με ελέγχω - χάνομαι - γίνομαι σκιά
""",
        published = True
            )

    add_song(
        title='Ό,τι αγαπώ είναι για λίγο',
        artist=artist_xasma,
        sender=user_bob,
        genre=Song.PUNK,
        content="""
F#5       A5               D5
Κάθε μου λέξη σε κρυμμένη σελίδα
     E5                       D5       E5
για εκείνο το πρωί που έμεινα μόνος να σκεφτώ
F#5              A5                         D5
και για το μυστικό μέσα στα μάτια σου που είδα
    B5                       C#5             E5
πως πίσω απ' τη γιορτή είσαι μαρτύριο και καταιγίδα

F#5              A5                    D5
Τώρα πως να στο δείξω ότι την ώρα που φεύγεις
     E5                      D5       E5
με εκείνους που λυπάμαι μου ζητάς να αγαπηθώ
F#5           A5                      D5
κι όσο είναι αρκετό που εύκολο δρόμο διαλέγεις
   B5                  C#5         E5             D5
αυτή η ανταμοιβή με φυλακίζει και πιέζει να δεχτώ
                  E5                        F#5
κάθε φτηνή περιγραφή αυτών που θα 'θελα να ζω
D5                    E5                A5
πάντα σ’ αγγίζω λίγο μέχρι να αρχίσω να πετώ

        C#5             D5
Μα ότι αγαπώ είναι για λίγο
         E5                   A5
για λίγο χάνομαι κι αρχίζω να πετώ
    C#5             D5
Ότι αγαπώ είναι για λίγο
         E5                     F#5
για λίγο χάνομαι κι αρχίζω να πετώ

F#5       A5                     D5
Γράψε μου λόγια από τα λόγια που ξέρεις
  E5                        D5          E5
κουβέντες που με βία αποστηθίζεις και θυμό
F#5     A5                      D5
Όσο πολλούς κι αν γύρω σου καταφέρεις
     B5                        C#5          E5
γι' αγάπη όταν μιλάς μέσα σου καίγεσαι και υποφέρεις

F#5         A5               D5
Κι έτσι τα βράδια αποζητάς προστασία
    E5                  D5       E5
σε μπαρ κοσμοπολίτικα ψαρεύεις σεβασμό
F#5       A5               D5
Ξέρεις, εκεί δε ζητιανεύω αξία
    B5                     C#5                   E5       D5
Θα μείνω απ' αυτούς στις γειτονιές που σπέρνουν άγριο χορό
                    E5                       F#5
Γράψε για μένα αποστροφή κι ένα κλουβί σαν φυλαχτό
D5                  E5                 A5
μέσα να μπαίνω λίγο μέχρι να αρχίσω να πετώ

Μα ότι αγαπώ είναι για λίγο...

<em>Κλείσιμο</em>
F#5 E5 D5
""",
        published = True
            )

    artist_spathia = add_artist('Ξύλινα Σπαθιά')

    add_song(
        title='Ρίτα',
        artist=artist_spathia,
        sender=user_bob,
        video='https://www.youtube.com/watch?v=O1dPCBoTUcI',
        genre=Song.ROCK,
        content="""
Em                          G D
Βρήκα χθες το βράδυ την αγάπη μου τη Ρίτα
κλώτσαγε τον Πύργο έριχνε πέτρες στα καράβια
κοίτα με στα μάτια μη φοβάσαι λέει κοίτα
Ρίτα τι να δω μωρό μου έχουν μείνει άδεια

Ρίτα πως μπορείς να τα ξεχάσεις όλα εκείνα
τα όνειρα που κάναμε να φύγουμε παρέα
μου 'χες πει μαζί θα την περνάμε πάντα φίνα
πάντοτε οι δυο μας θα τη βγάζαμε ωραία

E      G
Η Ρίτα αλλάζει
 D            A
τώρα πια δεν την τρομάζει
E       G
η νύχτα τα φώτα
D            A
όχι πια, όχι όπως πρώτα

Ρίτα σ' ένα κόσμο από σίδερο κι ατσάλι
βρες μου ένα τρόπο να μη ντρέπομαι να ζήσω
Ρίτα μου 'χουν βάλει δυναμίτη στο κεφάλι
Ρίτα μην πεθαίνεις μη μ' αφήνεις να σ' αφήσω

Η Ρίτα το ξέρει
ακονίζει το μαχαίρι
Ρίτα σταμάτα, σταμάτα, σταμάτα
""",
        published=False
            )

    add_song(
        title='Test Song',
        artist=artist_xasma,
        sender=user_bob,
        genre=Song.ROCK,
        tabs=True,
        content="""
Εισαγωγή:

E-----------------------------------------------------------0------
B---------------------------------------------------------------0--
G------------------------------------------------------------------
D------------------------------------------------------------------
A---0---0---0-2-3-2-0--0--0--0-2-3-2-0--------3---3----------------
E---------------------------------------1---1---1---1---0----------

e|-----------------------------------------------------------------
b|-----------------------------------------------------------------
g|-----------------------------------------------------------------
d|-------------------------------------------------------------7---
a|---0---0---0-2-3-2-0--0--0--0-2-3-2-0--------3---3-----------7---
e|---------------------------------------1---1---1---1---0-----5---

 Am    Bbsus4    Fb
Some lyrics lorem ipsum
lorem ipsum some other lyrics

    G11        F#dim13
lorem ipsum some other lyrics
lorem ipsum some other lyrics
""",
        published=True
            )

    # print out what we have added to the user
    print('Users:')
    for u in User.objects.all():
        print(u)

    print('\nSongs:')
    for a in Artist.objects.all():
        for s in Song.objects.filter(artist=a):
            print('{0} - {1}'.format(str(a), str(s)))


if __name__ == '__main__':
    print('starting chords population script...\n')
    populate()
