import re


"""
Regex to find URLs

Based on the work of Diego Perini (https://gist.github.com/dperini/729294)
(MIT License)

Python port by github user adamrofer

Changes: 
- made protocol identifier optional
- allow multiple dashes in host and domain name, as initially suggested by Diego Perini
- possible change: make host name optional to detect orf.at (error prone)
"""
URL_REGEX = re.compile(
    u""
    # protocol identifier
    u"(?:(?:https?|ftp)://)?"
    # user:pass authentication
    u"(?:\S+(?::\S*)?@)?"
    u"(?:"
    # IP address exclusion
    # private & local networks
    u"(?!(?:10|127)(?:\.\d{1,3}){3})"
    u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    u"|"
    # host name
    u"(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    u"(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
    u")"
    # port number
    u"(?::\d{2,5})?"
    # resource path
    u"(?:/\S*)?"
    u""
    , re.UNICODE)

"""
Valid unicodes in decimal including space, digits and latin letters
"""
VALID_UNICODES = ([]
                  + [32]                    # space
                  + [10, 12, 13, 133, 8233, 8232] # line breaks
                  + list(range(48, 58))     # digits
                  + list(range(65, 91))     # capital letters
                  + list(range(97, 123))    # small letters
                  + list(range(192, 215))   # latin extended
                  + list(range(216, 247))   # latin extended
                  + list(range(248, 688))   # latin extended
                )

"""
Additional stopwords for german and english.
These lists were generated by showing the difference between the Top-n most common words in the language and the list 
of stopwords for the language provided by nltk, with n being the size of the list of stopwords.
Afterwards some words were manually removed because they might be common in the text corpus but are important 
nonetheless, e.g. 'berlin' or 'love'.
"""
ADDITIONAL_STOPWORDS = {
    'german': ['etwa', 'wer', 'gerade', 'bitte', 'nie', 'steht', 'gehen', 'sagen', 'jahren', 'beim', 'sehen', 'ersten',
               'stadt', 'geht', 'heute', 'kommen', 'erst', 'recht', 'bereits', 'tag', 'sei', 'frage', 'wirklich',
               'zeit', 'wegen', 'ja', 'the', 'gar', 'ab', 'wäre', 'lassen', 'warum', 'drei', 'neue', 'müssen', 'kommt',
               'viele', 'sowie', 'macht', 'mal', 'seit', 'wurden', 'wurde', 'weiss', 'jedoch', 'dass', 'konnte',
               'dafür', 'genau', 'immer', 'hätte', 'einfach', 'jahre', 'menschen', 'neuen', 'leben', 'uhr', 'gute',
               'ganz', 'teil', 'gut', 'hast', 'wohl', 'gemacht', 'dabei', 'leute', 'gibt', 'besser', 'mehr', 'jahr',
               'geben', 'of', 'schon', 'welt', 'zwei', 'vielleicht', 'ende', 'deutschland', 'denen', 'ziemlich'],

    'english': ['year', 'first', 'going', 'never', 'best', 'old', 'last', 'way', 'part', 'may', 'want', 'world', 'need',
                'man', 'people', 'like', 'around', 'another', 'get', 'work', 'say', 'think', 'little', 'take', 'better',
                "i'm", 'im', 'good', 'three', 'still', 'make', 'great', 'state', 'day', "can't", 'cant', 'life', 'used',
                'time', 'must', 'find', 'since', 'really', 'us', 'well', 'would', 'also', 'got', 'new', 'see', "that's",
                "thats", 'could', 'home', 'many', 'always', 'come', 'right', 'go', 'years', 'made', 'one', 'two',
                'said', 'look', 'long', 'something', 'high', 'even', 'much', 'every', 'know', 'use', 'back']
}

UNSUPPORTED_LANGS = ['ja', 'ko', 'zh', 'yue']

BEST64_RULES = [":", "r", "u", "T0", "$0", "$1", "$2", "$3", "$4", "$5", "$6", "$7", "$8", "$9", "$0 $0", "$0 $1",
                "$0 $2", "$1 $1", "$1 $2", "$1 $3", "$2 $1", "$2 $2", "$2 $3", "$6 $9", "$7 $7", "$8 $8", "$9 $9",
                "$1 $2 $3", "$e", "$s", "] $a", "] ] $s", "] ] $a", "] ] $e $r", "] ] $i $e", "] ] ] $o", "] ] ] $y",
                "] ] ] $1 $2 $3", "] ] ] $m $a $n", "] ] ] $d $o $g", "^1", "^e ^h ^t", "o0d", "o0m o1a", "so0", "si1",
                "se3", "D2", "D2 D2", "D3", "D4", "'5 D3", "'5 $1", "]", "] ]", "] ] ]", "] ] ] d", "] ] D1 ]",
                "+5 ] } } } } '4", "O02 { { { { { {", "} ] ] {", "} } -0 O12", "} } }", "} } } } '4", "} } } } } '5",
                "} } } } } } Y4 '4 d", "*04 +0 '4", "*05 O03 d '3 p1", "+0 +0 +0 +0 +0 +0 +0 +0", "+0 +0 +0 O12",
                "Z4 '8 O42", "Z5 '6 O31 ] p1", "Z5 *75 '5 { O02", "d O28 Y4 '4 d", "f *A5 '8 O14", "p2 '7 p1 O58",
                "O14 d p2 '6"]
